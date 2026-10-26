from types import SimpleNamespace

from app import ask


def test_interactive_keeps_chat_history(monkeypatch, capsys):
    questions = []
    responses = iter(
        [
            SimpleNamespace(
                text="最初の回答",
                usage_metadata=SimpleNamespace(prompt_token_count=3, candidates_token_count=4),
            ),
            SimpleNamespace(
                text="続きの回答",
                usage_metadata=SimpleNamespace(prompt_token_count=8, candidates_token_count=5),
            ),
        ]
    )

    class FakeChat:
        def send_message(self, question):
            questions.append(question)
            return next(responses)

    class FakeClient:
        def __init__(self, api_key):
            self.chats = self

        def create(self, model):
            return FakeChat()

    prompts = iter(["最初の質問", "続けて質問", "終了"])
    monkeypatch.setattr(ask.genai, "Client", FakeClient)
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    monkeypatch.setattr("builtins.input", lambda _: next(prompts))

    ask.interactive()

    output = capsys.readouterr().out
    assert questions == ["最初の質問", "続けて質問"]
    assert "最初の回答" in output
    assert "続きの回答" in output
    assert "[tokens] 入力: 3, 出力: 4" in output
    assert "[tokens] 入力: 8, 出力: 5" in output