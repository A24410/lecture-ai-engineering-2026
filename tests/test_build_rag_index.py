"""実SQLiteと固定ベクトルで、索引作成から検索までを確認する。APIは呼ばない。"""

import json
from unittest.mock import Mock

import pytest

from app import retrieval
from scripts.build_rag_index import build_index


@pytest.fixture
def materials(tmp_path):
    source = tmp_path / "lectures.json"
    source.write_text(json.dumps([
        {"id": f"lec{n:02d}-main", "title": f"講義{n}", "content": [
            {"section": "章", "content": [
                {"id": f"lec{n:02d}-main-p001", "title": f"ページ{n}",
                 "page": 1, "content": f"本文{n}"}]}]}
        for n in (1, 2, 5)
    ], ensure_ascii=False), encoding="utf-8")
    return source, tmp_path / "index.sqlite3"


def test_built_index_can_be_searched(materials, monkeypatch):
    source, database = materials
    texts = []

    def embed(text, task):
        assert task == "RETRIEVAL_DOCUMENT"
        texts.append(text)
        return [1, 0] if "本文1" in text else [0, 1]

    result = build_index(source, database, embedder=embed)
    assert result["pages"] == 2  # 第5回の資料は検索対象に含めない
    assert all("章" in text and "ページ" in text for text in texts)
    monkeypatch.setattr(retrieval, "RAG_DB", database)
    monkeypatch.setattr(retrieval, "RAG_SOURCE", source)
    monkeypatch.setattr(retrieval, "embed_text", lambda *_: [1, 0])
    hits = retrieval.search("質問")
    assert [h["page_id"] for h in hits] == ["lec01-main-p001", "lec02-main-p001"]
    assert hits[0]["content"] == "本文1"
    assert hits[0]["distance"] == pytest.approx(0)


def test_search_includes_deduplicated_neighbors_from_same_document():
    pages = [
        {"page_id": f"lec01-main-p00{page}", "document_id": "lec01-main", "page": page}
        for page in range(1, 6)
    ]
    pages.append({"page_id": "lec02-main-p001", "document_id": "lec02-main", "page": 1})
    hits = [
        {**pages[1], "distance": 0.1},
        {**pages[3], "distance": 0.2},
    ]

    results = retrieval._include_neighbor_pages(hits, pages)

    assert [page["page_id"] for page in results] == [
        "lec01-main-p002", "lec01-main-p004", "lec01-main-p001",
        "lec01-main-p003", "lec01-main-p005",
    ]
    shared_neighbor = next(page for page in results if page["page_id"] == "lec01-main-p003")
    assert shared_neighbor["context_for"] == ["lec01-main-p002", "lec01-main-p004"]


def test_graph_prioritizes_query_matched_terms_and_keeps_unmatched_near_pages(tmp_path, monkeypatch):
    pages = [
        {"page_id": "seed", "document_id": "lec01-main", "title": "起点", "page": 1, "content": "起点本文"},
        {"page_id": "near", "document_id": "lec01-main", "title": "隣接ページ", "page": 2, "content": "隣接本文"},
        {"page_id": "relevant", "document_id": "lec01-main", "title": "LoRAの説明", "page": 3, "content": "関連本文"},
    ]
    graph = {
        "nodes": [
            {"id": page["page_id"], "kind": "page", "title": page["title"]}
            for page in pages
        ] + [{"id": "term:lora", "kind": "term", "title": "LoRA"}],
        "edges": [
            {"source": "seed", "target": "near", "relation": "next_page"},
            {"source": "seed", "target": "term:lora", "relation": "mentions"},
            {"source": "term:lora", "target": "relevant", "relation": "mentions"},
        ],
    }
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(graph), encoding="utf-8")
    monkeypatch.setattr(retrieval, "RAG_GRAPH", graph_path)
    monkeypatch.setattr(retrieval, "load_pages", lambda *_: pages)
    monkeypatch.setattr(retrieval, "_search_hits", lambda *_: [{"page_id": "seed", "distance": 0.1}])
    monkeypatch.setattr(retrieval, "GRAPH_START_K", 1)

    results = retrieval.search_graph("LoRAとは？")

    assert [page["page_id"] for page in results["expanded"]] == ["relevant", "near"]
    assert results["expanded"][0]["query_matched_terms"] == ["LoRA"]
    assert results["expanded"][0]["hops"] == 2
    assert results["expanded"][1]["query_matched_terms"] == []

    no_term_match = retrieval.search_graph("未登録の質問")
    assert [page["page_id"] for page in no_term_match["expanded"]] == ["near", "relevant"]


def test_existing_index_survives_failed_rebuild(materials):
    source, database = materials
    build_index(source, database, embedder=lambda *_: [1, 0])
    before = database.read_bytes()
    embed = Mock(side_effect=RuntimeError("埋め込みに失敗"))
    with pytest.raises(FileExistsError):
        build_index(source, database, embedder=embed)
    embed.assert_not_called()
    with pytest.raises(RuntimeError, match="埋め込みに失敗"):
        build_index(source, database, rebuild=True, embedder=embed)
    assert database.read_bytes() == before
    assert not list(database.parent.glob(".rag-build-*"))
