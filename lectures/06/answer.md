# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：glossary_search_glossary
- STEP 2 の [tool call]：[tool call]   glossary_search_glossary({'query': '3レベル'})
- STEP 3 の [tool call]：
  [tool call]   fetch_fetch({'url': 'https://modelcontextprotocol.io/'})
  [tool call]   glossary_search_glossary({'query': 'Model Context Protocol'})
- STEP 4 の [tool call]：[tool call]   aws_aws___search_documentation({'search_phrase': 'Amazon S3 versioning overview', 'topics': ['general']})
- 気づき・疑問：STEP 1 の一覧で glossary_search_glossary、fetch_fetch、aws_ で始まるツールを確認。STEP 3 ではfetchに加えて用語集ツールも呼び出された。

## 宿題

<!-- 各レベルの結果を個別に記録しています。 -->

### 基礎

- 取り組んだレベル：基礎
- やったこと：`app/mcp_server.py` で `get_lecture_summary` を MCP ツールとして公開しました。
- 結果：一覧に `glossary_get_lecture_summary` が追加され、「第2回では何を学びますか？」で呼び出されました。主題はファインチューニングと LoRA でした。
- 気づき・疑問：エージェント側を変更しなくても、MCP サーバーが公開するツールを追加すると一覧に反映されました。

### 実装

- 取り組んだレベル：実装
- やったこと：`make_quiz` を MCP ツールとして公開し、用語集にない回ではクイズを作れないことと利用できる回を返すようにしました。
- 結果：「第99回のクイズを作って」で `glossary_make_quiz` が呼び出され、ツールは「第99回のクイズは作れません。用語集にある回: 1, 2, 3, 4, 6」を返しました。モデルは利用できる回を案内しました。
- 気づき・疑問：`return` のメッセージは `[tool return]` としてモデルに渡りました。`raise` した場合の `[tool error]` との違いも確認したいです。

### 発展

- 取り組んだレベル：発展
- やったこと：2026-11-23 に VS Code の公式 MCP 設定ドキュメントを調べ、演習の `app/mcp_servers.json` と比較しました。
- 結果：VS Code の Copilot 用設定は、ユーザー全体なら `~/.copilot/mcp-config.json`（または `$COPILOT_HOME/mcp-config.json`）、ワークスペース共有ならルートの `.mcp.json` です。どちらも `mcpServers` 形式ですが、コマンド起動には `"type": "stdio"`、URL 接続には `"type": "http"` が必要です。演習の設定は `"command"` または `"url"` で接続方法を区別し、`type` は書きません。VS Code では UI の **Chat: Open Customizations** → **MCP Servers** から追加する方法もあります。参照：[VS Code MCP configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration.md)
- 気づき・疑問：VS Code の Copilot 用設定はユーザー全体とワークスペース共有を選べます。演習の設定ファイルは `app.mcp_agent.py` 用なので、VS Code の設定ファイルとは別です。
