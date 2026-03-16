# Manager: Engineer PR レビューワークフロー

## ゴール

- Engineer が作成した実装 PR について、
  - CI 状態・Acceptance Criteria・要件（docs/）との整合性を確認し、
  - Approve または Request Changes を判断する。
- 結果に応じて、次に呼ぶべきロール（Engineer 再実装 or 次タスク選定）をユーザーに案内する。

---

## 手順 1: PR と関連 Issue を把握する

1. ユーザーから対象 PR 番号を受け取る（例: `#23`）。
2. `gh-manager pr view <pr_number>` で概要と本文を確認し、
   - どの Issue を対象としているか（`Closes #<issue_number>` など）を特定する。
3. 対象 Issue を `gh-manager issue view <issue_number>` で開き、
   - タイトル
   - ラベル（`task` / `setup` / `refactor` など）
   - Requirements（R1, R2, ...）
   - Acceptance Criteria
   を箇条書きで整理する。

---

## 手順 2: CI 状態の確認

1. `gh-manager pr view <pr_number> --json statusCheckRollup` などで CI 状態を確認する。
2. テストや Lint が失敗している場合:
   - コードレビューを行う前に、「まず CI を修正してからレビュー」とする。
   - `gh-manager pr review <pr_number> --request-changes` を実行し、
     - レビューコメントで「CI が失敗しているので、`make test` / `make lint` などを修正してから再度レビュー依頼を出してほしい」ことを伝える。
   - 最後に、Engineer を呼び出すアクションブロックをユーザーに提示する（手順 4-A のブロックを利用）。

---

## 手順 3: ロジック・要件のレビュー（CI が Green の場合のみ）

1. PR 本文の Self-Walkthrough を確認する：
   - Issue に書かれた Requirements（R1, R2, ...）が、Self-Walkthrough 内で **明示的に参照されているか** を確認する。
     - 例: 「R1: ◯◯ → 対応コード: ..., テスト: ...」のように、Rn ごとの対応が書かれているか。
   - 対応が曖昧、または一部の Rn が言及されていない場合は、その点を修正要求候補としてメモしておく。
2. `gh-manager pr diff <pr_number>` や `git diff` でコード差分を確認する：
   - 各 Requirement（R1, R2, ...）が、実装の変更点とテストで実際に満たされているか。
   - Issue の Acceptance Criteria と差分内容が対応しているか。
   - docs/（`docs/REQUIREMENT.md`, `docs/USE_CASES.md` など）に書かれた要件・制約と矛盾していないか。
   - 明らかなバグ・セキュリティ上の問題・設計方針からの逸脱がないか。
3. Setup 系 Issue（`setup` ラベル）の場合は特に次を確認する：
   - Makefile / CI / Lint / Format / ROADMAP などの変更が、Issue の「作業内容」に書かれた方針どおりか。
   - Acceptance Criteria に列挙されたコマンド（`make setup` / `make test` / `make lint` / `make format` など）に対応する設定・ジョブが正しく定義されているか。
4. todo コメントやデバッグ用コード（`console.log` / 一時的な print など）が残っていないかを確認する。

---

## 手順 4: 結果に応じてレビューする

### 4-A. 修正が必要な場合（Request Changes）

1. 修正点を箇条書きで整理する：
   - どの Requirement（R1, R2, ...）が Self-Walkthrough / テスト / 実装で十分にカバーされていないか。
   - どの Acceptance Criteria が満たされていないか。
   - どのコードが docs/ や Issue の意図とズレているか。
   - Self-Walkthrough の説明が不十分 / 曖昧な点。
2. `gh-manager pr review <pr_number> --request-changes` を実行し、
   - 上記の内容をレビューコメントとして添付する。
3. ユーザーに、Engineer を呼び出すためのアクションブロックを提示する：

   ```md
   ::: action 🛑 User Action Required
   **Status:** Engineer PR Review (REJECTED)
   **Next Step:** すでに利用している Engineer 用チャットを開き、以下のプロンプトをそのまま送信してください。
   **Next Prompt:**
   > PR #<pr_number> に対して Manager から修正要求が出ています。  
   > レビューコメントを読み、Issue #<issue_number> の Requirements / Acceptance Criteria をすべて満たすように修正してください。
   :::
   ```

### 4-B. 問題がない場合（Approved）

1. `gh-manager pr review <pr_number> --approve` を実行する。
2. 必要であれば、「Acceptance Criteria を満たしており、docs/ とも矛盾がない」ことを短くコメントする。
3. ユーザーに、PR をマージし、次のタスクへ進むためのアクションブロックを提示する：

   ```md
   ::: action 🛑 User Action Required
   **Status:** Engineer PR Review (APPROVED)
   **Next Step:** GitHub 上で PR #<pr_number> をマージしてください。  
   マージ後、同じ Manager 用チャットで次のコマンドを実行して、次に着手すべき Issue を決めてください。
   **Next Prompt:**
   > docs/ の要件・設計 PR (#<pr_number>) がマージされました。  
   > /manager-create-task-issue docs/REQUIREMENT.md と関連ドキュメントをもとに、最初の実装用 Issue（例: 初期セットアップ / 最初の UC）を作成してください。
   :::
   ```