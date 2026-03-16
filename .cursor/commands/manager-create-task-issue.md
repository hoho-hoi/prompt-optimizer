# Manager: Engineer PR マージ後の次 Issue 選定ワークフロー

## ゴール

- Engineer の実装 PR マージ後に、
  - 既存の Issue バックログを確認し、
  - 次に着手すべき Issue を 1 件選ぶ。
  - バックログが空なら、次マイルストーン用の Issue バッチ（3〜5 件）を追加で作る。
- 最後に、選んだ Issue から Engineer を動かせる状態にする。

---

## 手順 1: 状況の確認

1. 直前に自分がレビューし、ユーザーにマージしてもらった Engineer PR（例: `#32`）を前提とする。
2. 必要に応じて `gh-manager pr view <pr_number>` で概要を確認し、
   - `Closes #<issue_number>` などから、どの Issue が解決されたかを特定する。
3. `gh-manager issue view <issue_number>` を見て、
   - その Issue の種類（`setup` / `task` / `refactor` など）と、
   - どういう範囲が完了したのかを簡単に把握する。

---

## 手順 2: バックログの確認と必要に応じた次マイルストーン設計

1. `gh-manager issue list` を用いて、まだ open の Issue を確認する。
   - 特に `task` / `setup` / `refactor` などのラベル付き Issue を見る。
2. 「今すぐ着手できる Issue が存在するか」で分岐する：
   - **A. 今すぐ着手できる Issue が存在する場合**
     - そのまま手順 3 に進む。
   - **B. 今すぐ着手できる Issue が存在しない場合（バックログがほぼ空、またはすぐに取り組める粒度の Issue がない場合）**
     - 次の手順で「次マイルストーン用の Issue バッチ」を作成してから、手順 3 に進む：
       1. `docs/` を読み、まだ実装していない UC / 機能 / 非機能要件を洗い出す。
       2. 直近の「次マイルストーン」として、まとめたい単位を 1 つ決める。
          - 例: 「ゲームの基本プレイが最後までできる」「設定画面を整える」など。
       3. そのマイルストーンを構成する Issue を 3〜5 件程度に分解する：
          - 各 Issue に、タイトル / 短い説明 / Acceptance Criteria を含める。
       4. `gh-manager issue create` を想定して、これらの Issue を順に登録する（ラベルも付与する）。

---

## 手順 3: 次に着手すべき Issue を 1 件選び、Engineer を呼び出す

1. open な Issue の中から、次を考慮して「次に着手すべき 1 件」を選ぶ：
   - 直近のマイルストーンや UC に対応しているか
   - 現在の実装状態から自然に進められるか（依存関係）
2. 選んだ Issue 番号を `<next_issue_number>` とし、ユーザーに Engineer を呼び出すためのアクションブロックを表示する：

   ```md
   ::: action 🛑 User Action Required
   **Status:** 次に着手すべき Issue を選定済み
   **Next Step:** 新しいチャットを開き、Engineer ロールを呼び出してください。
   **Next Prompt:**
   > @ai-engineer.mdc /engineer-task 次の Issue #<next_issue_number> から実装を進めてください。
   :::
   ```