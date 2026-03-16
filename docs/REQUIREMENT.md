# プロンプト改善 CLI / アプリ 要件定義

このドキュメントは、本プロダクトの要件定義の主文書である。詳細は `DOMAIN_ER.md`、`INTERACTION_FLOW.md`、`ARCHITECTURE_DIAGRAM.md`、`USE_CASES.md` を参照する。

---

## 1. Overview (Goal / Scope)

### 1.1 Product Summary

- Goal:
  既存プロンプトを入力として受け取り、改善要否を判定し、必要な場合のみ最小限の編集で改善後プロンプトを返せるようにする。
- Target Users:
  日常的にプロンプトを書く開発者、Cursor / CLI ベースで AI を活用するユーザー、短く保守しやすいプロンプトを重視するユーザー、AI エージェント向けシステムプロンプトを改善したいユーザー。
- One-line Description:
  「必要なら直し、不要なら直さない」を原則に、判定・理由・最小差分の改善・差分確認・テスト検証を提供するプロンプト改善支援ツール。

### 1.2 Scope

- In Scope:
  CLI での単一改善実行、改善要否のみの判定、差分表示、テスト実行、回帰テスト、メトリクス算出、ローカル設定・ケース・結果・スナップショット管理、将来のローカルアプリ拡張を見据えた core と UI の分離。
- Out of Scope:
  あらゆるモデルに対する最適性能保証、複数 LLM の自動 A/B 実行、本番運用時の大規模分散処理、自動課金管理、外部 SaaS 依存を前提にした構成。

### 1.3 Success Criteria & Constraints

- Success Criteria:
  CLI で `judgment`、`reason`、`improved_prompt`、`changes` を取得できること、改善不要ケースで不用意な差分を作らないこと、改善必須ケースで本質的な不足を補えること、差分を確認できること、テストケース群と回帰確認を実行できること、出力が過度に冗長化しないこと。
- Constraints:
  `improvement_requests` は参考情報として扱い強制適用しないこと、追加より削除・統合・言い換えを優先すること、改善後が長くなる場合は増加を正当化できること、元の意図を不必要に変えないこと、判定と結果内容を一致させること、テスト可能な構造にすること。

---

## 2. Domain Model (Domain)

### 2.1 Domain Entities

- Domain ER Diagram:
  `DOMAIN_ER.md` を参照。

### 2.2 Domain Notes (Optional)

- Notes:
  1 件の改善要求は `ImproveRequest` を単位として扱う。
  `improvement_requests` と `io_examples` は評価材料であり、改善内容へそのまま転記してはならない。
  `ImproveResult.judgment` が `改善不要` の場合、`improved_prompt` は元入力と同一であり、`changes` は `なし` でなければならない。
  テストは完全一致ではなく、振る舞い要件とルーブリック評価で品質を判定する。

---

## 3. Interaction / UI / Operations

### 3.1 Interaction State Flow

- Interaction State Diagram:
  `INTERACTION_FLOW.md` を参照。

### 3.2 Public Operations / APIs

| OP_ID | Interface / Path / Command | Summary |
|-------|----------------------------|---------|
| `OP_IMPROVE_PROMPT` | `prompt-improver improve --input input.json` / `cat prompt.md \| prompt-improver improve` | 判定、理由、改善後プロンプト、変更点、必要に応じて diff / metrics を返す |
| `OP_JUDGE_PROMPT` | `prompt-improver judge --prompt ./prompt.md` | 改善後プロンプトを返さず、判定と理由のみ返す |
| `OP_SHOW_DIFF` | `prompt-improver diff --prompt ./prompt.md --output ./result.json` | 元プロンプトと改善後プロンプトの差分を表示する |
| `OP_RUN_TESTS` | `prompt-improver test --cases ./tests/cases` | テストケース群に対して振る舞い検証を実行する |
| `OP_RUN_REGRESSION` | `prompt-improver regression --suite default` | 既存ケースに対する品質劣化の有無を確認する |

### 3.3 Use Cases

- Key Use Case IDs:
  `UC_IMPROVE_PROMPT`
  `UC_JUDGE_PROMPT`
  `UC_REVIEW_DIFF`
  `UC_RUN_TEST_CASES`
  `UC_RUN_REGRESSION`

---

## 4. Architecture

### 4.1 Components & Data Flow

- Architecture Diagram:
  `ARCHITECTURE_DIAGRAM.md` を参照。

### 4.2 Storage Scope Policy

- Ephemeral:
  入力正規化の中間値、目的推定結果、評価途中の一時データ、差分計算途中データ。
- Session:
  進行中の改善要求、アプリ編集中の未確定入力、実行中ジョブの状態。
- DeviceLocal:
  設定ファイル、テストケース、実行結果、レポート、スナップショット、キャッシュ、ローカルアプリの下書き保存データ。
- UserPersistent:
  初期バージョンでは必須要件なし。
- GlobalPersistent:
  初期バージョンでは必須要件なし。外部 SaaS 依存を前提としない。

### 4.3 Non-Functional Requirements (Architecture-related)

- Performance / Throughput:
  単一改善リクエストは通常数秒から十数秒程度で返せること。テストスイートは並列実行可能であること。同一入力の再評価コストを下げるためキャッシュを持てること。
- Security / Authentication / Authorization:
  ハードコードされた秘密情報を持たず、API 設定は環境変数または設定ファイルで扱うこと。改善対象プロンプトや設定値の誤記録を避け、不要な外部送信を前提にしないこと。
- Availability / Reliability / Backup:
  モデル呼び出し失敗時に実行単位で失敗を明示できること。テスト・回帰実行時にケース単位の結果を追跡できること。スナップショットは比較可能な形で保持できること。
- Observability (Logging / Metrics / Tracing / Alerting):
  入力、出力、メトリクス、失敗タグ、エラーを記録できること。テスト失敗時に原因追跡しやすいこと。
- Other NFRs:
  改善ロジックと出力整形ロジックを分離すること。プロンプト定義を差し替え可能にすること。将来的に複数モデル比較、自動評価器差し替え、エージェントワークフロー統合へ拡張可能であること。