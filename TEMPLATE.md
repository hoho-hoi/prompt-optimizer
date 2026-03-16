# Project Design: Cursor × GitHub CLI "Self-Validating" AI Development Ecosystem

## 1\. 概要 (Executive Summary)

本プロジェクトは、AIコードエディタ **Cursor** と **GitHub CLI**、そして **CI (GitHub Actions)** を組み合わせ、論理的整合性と品質を担保しながらソフトウェア開発を行う「半自律型AI開発エコシステム」の設計書です。

このシステムの核心は、単一のAIにすべてを任せるのではなく、**「要件定義」「管理・レビュー」「実装」という3つの役割（ロール）を明確に分割し、システム的に手順を強制する**点にあります。これにより、LLM特有の「幻覚（ハルシネーション）」や「自己正当化」を防ぎ、人間の関与を最小限かつ高レイヤーな意思決定のみに集中させます。

## 2\. コアコンセプト (Core Concepts)

### A. 役割の分断とコンテキストの分離

一人の人間に二重人格を演じさせるのではなく、\*\*完全に独立したチャットセッション（コンテキスト）\*\*で異なる役割をAIに実行させます。

  * **Architect:** 曖昧なアイデアを尋問し、定義書に落とし込む。
  * **Manager:** 実装コードを書かず、仕様管理とレビューに徹する（長期記憶）。
  * **Engineer:** Issueごとに生成され、タスク完了と共に破棄される（短期記憶）。

### B. CIによる客観的バリデーション

AIの「動くはずです」という言葉は信用しません。
**GitHub Actions** 上で `make test` (単体テスト) と `make lint` (静的解析) が通過しない限り、プルリクエスト（PR）のレビュー段階に進むことをシステム的に禁止します。

### C. Human-in-the-Loop の定型化

人間は「AIの思考」には介入しません。人間が行うのは以下の2点のみです。

1.  **承認と意思決定**（GO/NO-GOの判断）
2.  **物理的なスイッチング**（AIからの「指示サイン」に従い、適切なエージェントを呼び出す）

## 3\. ロール定義 (Role Definitions)

システムは `.cursor/rules/*.mdc` によって定義される以下の3つのロールで構成されます。

| ロール | 担当フェーズ | 振る舞い・権限 |
| :--- | :--- | :--- |
| **Architect**<br>(`ai-architect`) | 企画・要件定義 | **「尋問官」**<br>人間からの入力が曖昧な場合、`REQUIREMENT.md` が埋まるまで質問を繰り返す。定義が完了するまで実装フェーズへの移行を許可しない。 |
| **Manager**<br>(`ai-manager`) | タスク分解<br>レビュー<br>メタチェック | **「PM兼レビュアー」**<br>要件定義からIssueを作成する。PRに対し、コードそのものではなく「論理と要件の整合性」をレビューする。プロジェクト全体の設計歪みを検知する。 |
| **Engineer**<br>(`ai-engineer`) | 実装<br>テスト | **「使い捨て実装者」**<br>Issue単位で起動する。TDD（テスト駆動開発）を厳守し、PR作成時にはコードの変更理由を論理的に解説する義務を持つ。 |

## 4\. アーキテクチャ構成 (Architecture)

  * **Interface:** Cursor (Composer機能)
  * **Context Control:** ロールごとに「New Chat」を行い、コンテキストを汚染させない。
  * **Communication:** GitHub Issue / PR (全ての決定事項と議論はここに集約)
  * **Tools:**
      * `gh` (GitHub CLI): AIによるIssue/PRの操作
      * `make`: テスト・Lintコマンドの統一
      * `GitHub Actions`: CIによる品質ゲート

## 5\. 運用フロー (Workflow)

### Phase 0: 要件定義 (Architect)

1.  人間が「こういうアプリを作りたい」と Architect を呼び出す。
2.  Architect は `REQUIREMENT.md` のテンプレートに基づき、不足情報を人間にヒアリングする。
3.  全ての定義が埋まったら、Manager への引き継ぎサインを出す。

### Phase 1: タスク分解 (Manager)

1.  Manager は要件定義書を読み込み、実装可能な粒度の `task` Issue に分解して登録する。
2.  最初の Issue に着手するためのプロンプトを人間に提示する。

### Phase 2: 実装 (Engineer)

1.  人間は「Issue \#X をやって」と Engineer を呼び出す（**必ずNew Chat**）。
2.  Engineer は以下の厳格なループを実行する：
      * **TDD:** テスト作成 → 失敗(Red) → 実装 → 成功(Green)
      * **Lint:** `make lint` の通過
      * **Isolation:** `.env` 等の秘匿情報には触れない。実験コードはコミットしない。
3.  PRを作成する。この際、\*\*「要件ごとの論理的解決策（Self-Walkthrough）」\*\*を記述する。

### Phase 3: レビュー (Manager)

1.  **CI (GitHub Actions)** が自動実行される。失敗したPRはレビュー対象外。
2.  Manager はPRを読み、以下を確認する：
      * CIがGreenであるか。
      * PRの「論理的解決策」が理にかなっているか。
      * Diffが要件を満たしているか。
3.  問題なければマージ（Approve）、問題があれば修正指示（Reject）。

### Phase 4: メタレビュー (Manager)

1.  マージ完了後、Manager は「今回の変更がアーキテクチャ全体に悪影響（歪み）を与えていないか」を診断する。
2.  リファクタリングが必要と判断した場合、自らは修正せず、新たな `refactor` Issue を作成してバックログに積む。

## 6\. インターフェース仕様 (Human Interaction)

人間が迷わず操作できるよう、AIはアクションが必要なタイミングで必ず以下の\*\*「アクションブロック」\*\*を表示します。

```markdown
::: action 🛑 人間の操作が必要です
**状況:** [現在のステータス (例: PR作成完了)]
**操作:** [次に人間がすべき物理操作 (例: New Chatを開く)]
**次のプロンプト:**
(ここにあるテキストをコピーして、次のチャットに入力するだけ)
> @ai-manager.mdc PR #15 のレビューをお願いします。
:::
```

## 7\. ディレクトリ構造 (Project Structure)

```text
root/
├── .cursor/
│   └── rules/              # 各AIロールの振る舞い定義 (.mdc)
│       ├── ai-architect.mdc
│       ├── ai-manager.mdc
│       ├── ai-engineer.mdc
│       └── tech-stack.mdc  # 技術選定・コーディング規約
├── .github/
│   ├── workflows/          # CI定義 (push時に test/lint 実行)
│   ├── ISSUE_TEMPLATE/     # タスク定義用テンプレート
│   └── PULL_REQUEST_TEMPLATE.md # Self-Walkthrough記述用
├── REQUIREMENT.md          # アーキテクトが管理する要件定義書
├── ROADMAP.md              # マネージャーが管理する進捗表
├── Makefile                # コマンド集約 (test, lint)
└── src/                    # ソースコード
```

## 8\. 安全装置と制約 (Guardrails)

1.  **TDD & Lint 強制:** ローカルで `make test` `make lint` が通らないコードはPush禁止。さらにCIでダブルチェックを行う。
2.  **シーケンシャル処理:** 複数のIssueを同時に進行させない。常に「1つのIssue、1つのEngineerセッション」で完結させ、コンテキストの混濁を防ぐ。
3.  **秘匿情報の保護:** AIには `.env` などのCredentialファイルへのアクセス権限を与えず、モックデータでのテストを原則とする。