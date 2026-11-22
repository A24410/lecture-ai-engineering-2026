# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：第1回（素のLLM）は用語集を参照せず回答するのに対し、エージェントはツールで用語集を確認して回答する。
- `--trace` で見えたツール呼び出し（ツール名と引数）：make_quiz(lecture=2)
- 1つの質問での LLM 呼び出し回数（`requests`）：2
- 追加したツールと、docstring に書いた説明：
  ・追加ツール名：make_quiz
  ・docstringに書いた説明：「指定回の用語から確認問題と答えを返す」「復習用の問題を求められたときに使う」


## 宿題

- 取り組んだレベル：基礎
- やったこと：`app/tools.py` の `search_glossary` のdocstringを、一時的に「用語を1つずつ検索する指示」から、「関連する用語をまとめて検索する指示」に変更し、`--trace` 付きで「LoRAとQLoRAの違いは？」を質問した。
- 結果：変更前は `LoRA` と `QLoRA` を別々に検索して `tool_calls=2`、変更後は `LoRA QLoRA` をまとめて検索して `tool_calls=1` だった。LLM リクエスト数はどちらも2回。回答はいずれもLoRAとQLoRAの仕組みやメモリ効率を説明し、（関連する回：第2回）を出力した。
- 気づき・疑問：ツールのdocstringを変えると、検索語のまとめ方とツール呼び出し回数が変わったが、LLM リクエスト数は変わらなかった。

- 取り組んだレベル：実装
- やったこと：`save_learning_log` ツールを作成し、Pydantic AIで `requires_approval=True` を付けて登録した。
- 結果：テストで、承認前はログファイルが作成されず、承認後 `learning_log/` にmdファイルが作成されることを確認した。
- 気づき・疑問：テスト用の一時ディレクトリを用いることで実データを残さず保存結果を確認できる。

- 取り組んだレベル：発展（a）
- やったこと：`app/agent.py` の `INSTRUCTIONS` と `app/tools.py` の `search_glossary`・`get_lecture_summary`・`make_quiz` を使い、ADK の `Agent` で `adk_agent/glossary_agent/` を作成した。
- 結果：「LoRAとQLoRAの違いは？」に対し、Pydantic AI と ADK の両方が、「LoRAは低ランク行列で更新を学習し、QLoRAはベースモデルの重みを4ビットなどに量子化してメモリを節約する」と回答した。どちらも（関連する回：第2回）を出力した。Pydantic AI は `search_glossary({'query': 'LoRA QLoRA'})` を呼び、LLM リクエスト数は2回だった。
- 気づき・疑問：Pydantic AI では `Agent` を作成してから `tool_plain` でツールを登録するのに対し、ADK では `Agent` の引数 `instruction` と `tools` にまとめて渡す点。

- 取り組んだレベル：発展（b）
- やったこと：Pi v1.5.0 をCodespacesにインストールし、公式の `packages/coding-agent/src/core/system-prompt.ts` と AIE の `INSTRUCTIONS` を比較。
- 結果：ツールを無効にした状態で `gemini-3.5-flash-lite` に質問し、`READY` と応答することを確認した。
- 気づき・疑問：Pi の公開システムプロンプトは、コーディング支援、利用可能なツール、簡潔さやパス表示などの汎用ルールを含む。一方、AIE の `INSTRUCTIONS` は用語検索、講義要約、確認問題、宿題へのヒントなど講座固有のルールを含む。Pi側のプロンプトには実行環境に応じてプロジェクト指示・スキル・作業ディレクトリも追加される。