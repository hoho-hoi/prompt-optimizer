# Engineer: Issue 実装ワークフロー

## ゴール

- 指定された 1 件の Issue について、
  - Acceptance Criteria を満たす実装を行い、
  - `make test` / `make lint` を通したうえで PR を作成する。
- 行き詰まった場合は、Issue コメントで状況を共有し、Manager にエスカレーションする。

---

## 手順 1: Issue を読み、ブランチを切る

1. 対象 Issue 番号をユーザーから受け取る（例: `#12`）。
2. `gh-engineer issue view <issue_number>` の内容を読み、
   - タイトル
   - 説明
   - Acceptance Criteria
   を箇条書きで整理する。
3. 作業用ブランチを作成する（例）:
   - `git checkout -b feature/issue-<issue_number>-<short-summary>`

---

## 手順 2: TDD で実装する

1. まずテストから書く（または修正する）。
   - Acceptance Criteria をそのままテストケースに落とし込むイメージで、
     対応する `tests/` またはプロジェクト既定のテストディレクトリにテストを書く。
   - 「どの振る舞いが期待されているか」が読み取れる名前・構造にする。
2. `make test` を実行し、
   - 新しいテストが **失敗** していることを確認する。
   - ここでテストが通ってしまう場合は、テストが不十分な可能性を疑い、ケースを追加・強化する。
3. 実装コードを書く。
   - 対応する `src/` 等に、テストを Green にする最小限の実装を書く。
   - 大きなリファクタリングは避け、まずはテストを通すことを優先する。
4. 再度 `make test` を実行し、
   - すべてのテストが Green になることを確認する。
5. 必要であれば、リファクタリングを行う。
   - 振る舞いを変えずに内部構造を整理し、再度 `make test` を実行して Green を維持する。

> 行き詰まり判定の目安:
> - 同じテストが 5 回以上連続で失敗し、原因の仮説や修正方針が尽きていると判断したとき。

---

## 手順 3: Lint / Format を通す

1. プロジェクトに `make format` が定義されている場合は、`make format` を実行してコード整形を行う。
2. `make lint` を実行し、Lint エラーや警告をすべて解消する。
3. `git status` を確認し、
   - 不要なファイル（ログ、一時ファイル、scratch ディレクトリなど）がステージされていないか確認する。

---

## 手順 4: PR を作成する（成功パス）

1. 変更を commit する。
   - メッセージ例: `"Implement <short summary> for issue #<issue_number>"`
2. リモートに push する。
3. PR 本文を用意する。
   - `.github/PULL_REQUEST_TEMPLATE/engineer_requirements.md` に従う。
   - 少なくとも次の情報を含める：
     - `Closes #<issue_number>`
     - どの Acceptance Criteria を、どのテストとどの実装で満たしたかの対応表
       - 例:
         - AC1 → `tests/xxx.test.ts` の `<test name>` → `src/yyy.ts` の `<function>`
4. `gh-engineer pr create` を実行し、上記の本文を指定して PR を作成する（`--body` または `--body-file` を使用）。

5. PR を作成したら、ユーザーに「PR 番号」と「次に Manager を呼び出すためのプロンプト」を含むアクションブロックを表示する（例）:

   ```md
   ::: action 🛑 User Action Required
   **Status:** PR 作成完了
   **Next Step:** すでに利用している Manager 用チャットを開き、以下のプロンプトをそのまま送信してください。
   **Next Prompt:**
   > /manager-review-engineer PR #<pr_number> をレビューし、Issue #<issue_number> の Acceptance Criteria を満たしているか確認してください。
   :::
   ```

## 手順 5: 行き詰まった場合の対応（Block パス）

1. 「行き詰まり」と判断した場合は、PR を作らず、Issue にコメントする。
   - コメントには、少なくとも次を箇条書きで書く：
   - 失敗しているテスト名・テストファイル
   - 試したアプローチ（何をどのように変えたか）
   - それでも失敗している理由の仮説
   - 考えられる代替案（あれば）
2. コメントを投稿したあと、ユーザーに Manager ロールへのエスカレーションを促すアクションブロックを表示する（例）:

   ```md
   ::: action 🛑 User Action Required
   **Status:** Engineer 行き詰まり
   **Next Step:** すでに利用している Manager 用チャットを開き、以下のプロンプトをそのまま送信してください。
   **Next Prompt:**
   > /manager-escallation Issue #<issue_number> で Engineer が行き詰まりました。Issue コメントを読んで、次の方針を決めてください。
   :::
   ```

3. この状態では、PR を作成してはいけない。Manager の指示や Issue の更新を待ってから、改めて Engineer ロールを呼び出してもらう。