# Engineer: Setup Issue 実装ワークフロー

## ゴール

- `setup` ラベルが付いた Issue を 1 件ずつ確実に完了させる。
- Issue に書かれた「作業内容」と「Acceptance Criteria」に従って、
  開発環境・Makefile・Lint/Format・CI・ROADMAP などの初期セットアップを実装する。
- `make setup` / `make test` / `make lint` / `make format` など、指定されたコマンドが正常終了する状態で PR を作成する。

---

## 手順 1: Issue を読み、ブランチを切る

1. 対象 Issue 番号をユーザーから受け取る（例: `#12`）。
2. `gh-engineer issue view <issue_number>` の内容を読み、
   - タイトル
   - 概要
   - Requirements
   - Acceptance Criteria
   を箇条書きで整理する。
3. 作業用ブランチを作成する（例）:
   - `git checkout -b feature/issue-<issue_number>-<short-summary>`


---

## 手順 2: Issue の「作業内容」に従って実装する

1. Issue の「作業内容」を上から順に処理する。
   - Makefile / タスクランナーに関する指示があれば、そのターゲットやコマンドを実装・調整する。
   - Lint / Format / Test の導入・設定について指示があれば、そのツール・設定ファイルを追加・変更する。
   - CI に関する指示があれば、`.github/workflows/` 配下のワークフローを適切に作成・更新する。
   - ROADMAP など docs 系については、指定されたアウトライン・項目どおりに記述する。

---

## 手順 3: 自己チェック（ローカルコマンド）

1. Issue の Acceptance Criteria に列挙されているコマンドをすべて実行し、結果を確認する。
   - 例:
     - `make setup`
     - `make test`
     - `make lint`
     - `make format`
2. すべてのコマンドが正常終了することを確認する。
3. `git status` を確認し、
   - 不要ファイル（ログ、一時ファイルなど）がステージされていないことを確認する。

---

## 手順 4-A: PR を作成する（成功パス）

1. 変更内容を commit する。
   - メッセージ例: `"Setup project tooling for issue #<issue_number>"`.
2. ブランチを push する。
3. `gh-engineer pr create` を実行し、本文に必ず次を含める：
   - `Closes #<issue_number>`
   - この PR で実施した Setup 内容（Makefile・テスト・Lint/Format・CI・ROADMAP など）の要約
   - Acceptance Criteria と、どのコマンドで確認したかの対応（簡潔でよい）

4. 最後に、ユーザー向けに Manager 呼び出し用アクションブロックを表示して終了する：

   ```md
   ::: action 🛑 User Action Required
   **Status:** Setup Issue 用 PR 準備完了
   **Next Step:** すでに利用している Manager 用チャットを開き、以下のプロンプトをそのまま送信してください。
   **Next Prompt:**
   > /manager-review-engineer Setup Issue #<issue_number> に対応する PR #<pr_number> をレビューし、Acceptance Criteria を満たしているか確認してください。
   :::
   ```


---

## 手順 4-B: 行き詰まった場合（Block パス）

1. Setup 作業の途中で、次のような状態になった場合は「行き詰まり」とみなす：
   - Acceptance Criteria にあるコマンド（例: `make test`, `make lint` など）が、複数回の修正を行っても通らない。
   - ツール選定や構成について、Issue や `docs/` だけでは判断ができない。
   - CI の制約などにより先に進めないが、自力で解決策を決められない。

2. 行き詰まりと判断したら、PR は作らず、Issue にコメントを投稿する：
   - コメントには次を箇条書きで書く：
     - 現在失敗しているコマンドやテスト（例: `make test` のエラー概要）
     - 試した手順（どの設定やコマンドをどう変えたか）
     - それでも解決していない理由の仮説
     - 考えられる代替案（あれば）

3. コメントを投稿したあと、ユーザー向けに Manager 呼び出し用アクションブロックを表示する：

   ```md
   ::: action 🛑 User Action Required
   **Status:** Setup Issue で Engineer が行き詰まり
   **Next Step:** すでに利用している Manager 用チャットを開き、以下のプロンプトをそのまま送信してください。
   **Next Prompt:**
   > /manager-escallation Setup Issue #<issue_number> で Engineer が行き詰まりました。  
   > Issue コメントを読んで、要件・構成・Acceptance Criteria の見直しや次の方針を決めてください。
   :::
   ```

4. Manager の方針がコメントとして決まるまで、この Issue について新たな PR は作成しない。