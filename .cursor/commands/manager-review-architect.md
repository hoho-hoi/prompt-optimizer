# Manager: Architect PR レビューワークフロー

## ゴール

- Architect が作成した「要件・設計ドキュメント PR」をレビューし、
  - 問題があれば修正点をコメントし、Request Changes を出す。
  - 問題がなければ Approve し、次のステップ（Issue 作成・Engineer 呼び出し）につなげる。

---

## 手順 1: PR の内容を把握する

1. ユーザーから対象 PR 番号（例: `#15`）を受け取る。
2. `gh-manager pr view <pr_number>` で PR の概要・本文を確認し、
   - この PR が「docs/ の要件・設計ドキュメント」であることを確認する。
3. `gh-manager pr view <pr_number> --json files` または `gh-manager pr diff <pr_number>` などで、
   - どの docs/ ファイルが変更されているかを把握する。
   - 例: `docs/REQUIREMENT.md`, `docs/USE_CASES.md`, `docs/DOMAIN_ER.md` など。

---

## 手順 2: docs/ の整合チェック

1. 変更された docs/ ファイルをすべて読み、PR の「レビュー観点 (Manager 向け)」に沿って内容をチェックする。
2. 特に UC_ID / OP_ID / STATE_ID などの識別子、用語・制約、公開 Operations、コンポーネント、In/Out of Scope、非機能要件、未確定事項や TODO の扱いが、`docs/` 配下の各ファイル間で矛盾していないかを重点的に確認する。

---

## 手順 3: 結果に応じてレビューする

### 3-A. 問題がある場合（修正要求）

1. 修正が必要な点を箇条書きで整理する：
   - どのファイルのどの部分が、どう問題なのか。
   - どう修正すべきか（方向性レベルで十分）。
2. `gh-manager pr review <pr_number> --request-changes` を行い、
   - 上で整理した内容をレビューコメントとして添付する。
3. ユーザーに、Architect を呼び出すためのアクションブロックを提示する：

   ```md
   ::: action 🛑 User Action Required
   **Status:** Architect PR Review (REJECTED)
   **Next Step:** すでに利用している Architect 用チャットを開き、以下のプロンプトをそのまま送信してください。
   **Next Prompt:**
   > Manager からのレビューコメントを反映して、docs/ 以下のドキュメントを修正してください。  
   > 対象 PR: #<pr_number>
   :::
   ```

### 3-B. 問題がない場合（承認）
1.	gh-manager pr review <pr_number> --approve で承認する。
2.	必要であれば、ユーザーに対して「この PR は docs/ の要件・設計として妥当」と短くコメントを残す。
3.	ユーザーに、PR をマージし、続いて Issue 作成や Engineer 呼び出しに進むためのアクションブロックを提示する：

   ```md
   ::: action 🛑 User Action Required
   **Status:** Architect PR Review (APPROVED)
   **Next Step:** GitHub 上で PR #<pr_number> をマージしてください。  
   マージ後、このチャットで以下のプロンプトをそのまま送信してください。
   **Next Prompt:**
   > docs/ の要件・設計 PR (#<pr_number>) がマージされました。  
   > /manager-create-setup-issue docs/REQUIREMENT.md と関連ドキュメントをもとに、最初の実装用 Issue（例: 初期セットアップ / 最初の UC）を作成してください。
   :::
   ```