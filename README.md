# prompt-improver

`prompt-improver` は、既存プロンプトを評価し、「必要なら直し、不要なら直さない」を原則に最小限の改善案を返す prompt improver です。

現時点で公開 CLI として実装されているのは `improve` のみです。README では、今すぐ使える操作だけを説明します。

## What It Does

- 既存プロンプトの改善要否を判定します。
- 判定理由を返します。
- 必要な場合だけ改善後プロンプトを返します。
- どこを変えたかを `changes` で要約します。

## Quick Setup

必要条件:

- `Python 3.12`
- [`uv`](https://docs.astral.sh/uv/)
- `make`

最短セットアップ手順:

`make setup` で開発用依存関係を同期します。

```bash
git clone <your-repository-url>
cd prompt-optimizer
make setup
```

必要な環境変数:

- `OPENAI_COMPATIBLE_BASE_URL`
- `OPENAI_COMPATIBLE_API_KEY`
- `PROMPT_IMPROVER_MODEL_NAME` (`gpt-4.1-mini` を上書きしたい場合のみ任意)

設定例:

```bash
export OPENAI_COMPATIBLE_BASE_URL="https://your-openai-compatible-endpoint.example/v1"
export OPENAI_COMPATIBLE_API_KEY="<YOUR_API_KEY>"
export PROMPT_IMPROVER_MODEL_NAME="gpt-4.1-mini"
```

実行前の前提:

- `prompt-improver improve` は raw text ではなく JSON payload を受け取ります。
- file input と standard input のどちらでも、少なくとも `originalPrompt` が必要です。

## Improve Command

`improve` は JSON を入力に取り、JSON を標準出力へ返します。

### File Input Example

`request.json`:

```json
{
  "originalPrompt": "Summarize this incident report.",
  "improvementRequests": [
    "Keep the response concise.",
    "Preserve technical accuracy."
  ],
  "additionalConstraints": [
    "Use plain language."
  ],
  "context": "Internal support workflow"
}
```

実行例:

```bash
uv run prompt-improver improve --input request.json
```

### Standard Input Example

standard input からも同じ JSON payload を渡せます。

```bash
printf '%s' '{
  "originalPrompt": "Draft a release note.",
  "improvementRequests": ["Make success criteria explicit."],
  "ioExamples": ["Input: changelog\nOutput: short release note"]
}' | uv run prompt-improver improve
```

### Output Example

```json
{
  "judgment": "改善推奨",
  "reason": "The prompt does not define the expected output format clearly.",
  "improved_prompt": "Draft a short release note with explicit success criteria.",
  "changes": "Added an explicit output format.\nAdded a clearer success criterion."
}
```

出力項目:

- `judgment`: 改善要否の判定です。現在の実装では `改善不要`、`改善推奨`、`改善必須` のいずれかです。
- `reason`: その判定になった理由です。
- `improved_prompt`: 判定結果に基づく改善後プロンプトです。`judgment` が `改善不要` の場合は元のプロンプトと同じ値になります。
- `changes`: 変更内容の要約です。変更がない場合は `なし` になります。

## Current Limitations

- 現在の公開 CLI は `improve` のみです。
- `improve` は JSON payload 前提であり、Markdown やプレーンテキストのプロンプトをそのまま standard input に流しても解釈しません。
- API の接続先と認証情報は環境変数で与える必要があります。秘密情報をリポジトリへ保存しないでください。

## Planned But Not Implemented Yet

以下の公開操作は要件上の候補ですが、現時点では未実装です。README 上でも「今後の予定」として扱ってください。

| Command | Status | Notes |
|---------|--------|-------|
| `judge` | 未実装 | 判定と理由のみを返す公開コマンドはまだありません。 |
| `diff` | 未実装 | 差分表示用の公開コマンドはまだありません。 |
| `test` | 未実装 | ケース実行用の公開コマンドはまだありません。 |
| `regression` | 未実装 | 回帰確認用の公開コマンドはまだありません。 |
