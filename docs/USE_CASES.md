# USE_CASES.md

## Use Cases

### UC-1

- UC_ID: `UC_IMPROVE_PROMPT`
- Title: プロンプトを最小編集で改善する
- Actor: プロンプト作成者

- Goal:
  元プロンプトの改善要否を総合判断し、必要な場合のみ最小限の差分で改善後プロンプトを得る。

- Precondition:
  `ImproveRequest.originalPrompt` が与えられている。`improvementRequests`、`ioExamples`、`additionalConstraints`、`context` は任意で与えられる。
- Postcondition:
  `ImproveResult` が生成される。`judgment` が `改善不要` の場合、`improvedPrompt` は元プロンプトと同一であり、`changes` は `なし` になる。

- States: [`STATE_INPUT_READY`, `STATE_NORMALIZING_INPUT`, `STATE_EVALUATING_PROMPT`, `STATE_GENERATING_IMPROVED_PROMPT`, `STATE_CALCULATING_OUTPUT`, `STATE_RESULT_READY`]

- Operations: [`OP_IMPROVE_PROMPT`]

- ErrorCases:
  - 必須入力が不足している場合は実行前に検証エラーとして終了する。
  - モデル呼び出しまたは内部評価に失敗した場合は結果を確定せず、失敗として返す。
  - 判定と出力内容が不一致な場合は不正な結果として扱い、結果を採用しない。

---

### UC-2

- UC_ID: `UC_JUDGE_PROMPT`
- Title: 改善要否だけを診断する
- Actor: プロンプト作成者

- Goal:
  改善後プロンプト生成を伴わず、改善不要かどうかとその理由だけをすばやく確認する。

- Precondition:
  `ImproveRequest.originalPrompt` が与えられている。
- Postcondition:
  判定結果と理由が返る。改善後プロンプトは公開結果として必須ではない。

- States: [`STATE_INPUT_READY`, `STATE_NORMALIZING_INPUT`, `STATE_EVALUATING_PROMPT`, `STATE_JUDGMENT_READY`]

- Operations: [`OP_JUDGE_PROMPT`]

- ErrorCases:
  - 入力ファイル形式が不正な場合は判定を行わずエラーを返す。
  - 判定理由が空の場合は不完全な結果として扱い、失敗にする。

---

### UC-3

- UC_ID: `UC_REVIEW_DIFF`
- Title: 変更差分と要点を確認する
- Actor: プロンプト作成者

- Goal:
  元プロンプトと改善後プロンプトの差分を確認し、何が本質的に変わったかを把握する。

- Precondition:
  `ImproveResult` が存在する。
- Postcondition:
  unified diff、side-by-side diff、変更要約のいずれかで差分を参照できる。

- States: [`STATE_RESULT_READY`, `STATE_DIFF_READY`]

- Operations: [`OP_SHOW_DIFF`]

- ErrorCases:
  - 比較対象の結果ファイルが存在しない場合は差分表示を行わずエラーを返す。
  - 改善不要結果で差分が存在する場合は不整合として扱う。

---

### UC-4

- UC_ID: `UC_RUN_TEST_CASES`
- Title: テストケース群で振る舞いを検証する
- Actor: 改善ロジックの保守者

- Goal:
  事前定義したケース群に対して改善エンジンを実行し、判定妥当性・最小変更性・簡潔性・安定性を評価する。

- Precondition:
  テストケースディレクトリが存在し、各ケースが `ImproveRequest` と期待条件を持つ。
- Postcondition:
  ケースごとの結果、ルーブリック得点、失敗タグ、集計レポートが得られる。

- States: [`STATE_TEST_CASES_READY`, `STATE_RUNNING_TESTS`, `STATE_TEST_REPORT_READY`]

- Operations: [`OP_RUN_TESTS`]

- ErrorCases:
  - ケース定義が壊れている場合は対象ケースを失敗として記録する。
  - 途中失敗時は `--fail-fast` 指定の有無に従って停止または継続する。

---

### UC-5

- UC_ID: `UC_RUN_REGRESSION`
- Title: 既存品質の劣化を確認する
- Actor: 改善ロジックの保守者

- Goal:
  改善ロジックまたはプロンプト定義を変更した後、既存ケースに対して品質悪化が起きていないことを確認する。

- Precondition:
  回帰スイートと比較対象スナップショットが存在する。
- Postcondition:
  スイート単位の pass / fail、差分のあるケース、更新が必要なスナップショットが判明する。

- States: [`STATE_TEST_CASES_READY`, `STATE_RUNNING_REGRESSION`, `STATE_TEST_REPORT_READY`]

- Operations: [`OP_RUN_REGRESSION`]

- ErrorCases:
  - 比較用スナップショットが欠落している場合は回帰判定を確定できない。
  - 品質スコア低下や禁止タグ発生時は回帰失敗として記録する。