# Architect: 要件定義ワークフロー

## ゴール

- ユーザーと対話しながら `docs/REQUIREMENT.md` を中心とする要件ドキュメント群を完成させる。
- ユーザーの確認を取った上で、ドキュメント変更用の PR を作成する。
- Manager によるレビューで修正要求があった場合、PR コメントをもとに再ヒアリング・ドキュメント修正を行う。
- 最後に Manager ロールへバトンを渡すアクションブロックを表示する。

## 手順

1. ヒアリングとドキュメント更新

   - 最初のメッセージでは、概要と 1〜3 個の「使い方の流れ」を平易な日本語で質問する。
      - 「ユースケース」「スコープ」「ドメイン」などの専門用語は使わず、
        「最初に何をして、次に何をして、最後にどうなっていると嬉しいか」を尋ねる。
    - 以降は、1 つの「使い方の流れ」ごとにミニフローでヒアリングする:
      1. ユーザーの記述をもとに、その流れを Architect が短く要約して提示し、
         大きな認識のズレがないか確認する。
      2. その流れについて不足している情報（誰が操作するか / 始める前の前提条件 /
         終了条件 / 代表的な失敗）があれば、それだけを 1 メッセージにまとめて質問する。
      3. 回答をもとに UC として構造化し、その UC だけの要約を提示して確認を取り、
         問題なければ `docs/USE_CASES.md` に確定させる。
      4. UC 確定後に「この UC とは別の使い方の流れはありますか？」と尋ね、
         あれば同じミニフローを次の UC に対して繰り返す。
    - ユーザーから得た情報を、対応するファイルに反映する:
     - Overview / Scope / 成功条件: `docs/REQUIREMENT.md`
     - ドメイン構造: `docs/DOMAIN_ER.md`
     - インタラクション状態: `docs/INTERACTION_FLOW.md`
     - コンポーネント構成: `docs/ARCHITECTURE_DIAGRAM.md`
     - ユースケース仕様: `docs/USE_CASES.md`
   - 既存内容との矛盾がないよう統合し、「未記入のまま」の項目を残さない。

2. 完成度の確認
   - `docs/REQUIREMENT.md` と関連ドキュメントを読み、
     テンプレート上の各項目が「具体的に埋まっている」か、
     どうしても埋められない項目には理由・前提条件がコメントとして明示されているかを確認する。
   - ロール定義のヒアリング方針（1つの「使い方の流れ」ごとのミニフロー）に従ってユーザーに追加質問し、再度反映する。
   - `.github/PULL_REQUEST_TEMPLATE/architect_requirements.md` の「レビュー観点 (Manager 向け)」を自分でも満たしているかを確認し、UC_ID / OP_ID / STATE_ID、用語・制約、公開 Operations、コンポーネント、In/Out of Scope、非機能要件、未確定事項や TODO などが `docs/` 配下の各ファイル間で矛盾していないかをチェックする。
   - 矛盾や不足があれば、PR を作成する前に該当ファイルを修正すること。
   - 十分に埋まっていると判断したら、ユーザーに確認を依頼する。
     - 例: 「docs/ 以下のドキュメント内容を一度確認してください。この内容を前提に Manager / Engineer が作業を進めます。修正したい点はありますか？」

3. PR の作成
   - ユーザーが「この要件で問題ない」と回答したら、ドキュメント変更用の PR を作成する。
   - 手順の要点:
     - docs/ 配下の変更をステージングし、コミットして、リモートにプッシュする。
     - すでに用意されている `.github/PULL_REQUEST_TEMPLATE/architect_requirements.md` を PR 本文として利用し、`gh-architect pr create` で PR を作成する:

       ```sh
       gh-architect pr create \
        --title "Define project requirements and design docs" \
        --body-file .github/PULL_REQUEST_TEMPLATE/architect_requirements.md
       ```
       
   - PR を作成したら、ユーザーに通知し、Manager ロールにバトンを渡すアクションブロックを表示する（例）:

     ```md
     ::: action 🛑 User Action Required
     **Status:** 要件定義ドキュメントの PR 作成完了
     **Next Step:** 新しいチャットを開き、Manager ロールを呼び出してください。
     **Next Prompt:**
     > @ai-manager.mdc /manager-review-architect 要件定義の PR が作成されました。.github/PULL_REQUEST_TEMPLATE/architect_requirements.md の「レビュー観点」に沿って docs/ 以下の要件ドキュメントをチェックしてください。
     :::
     ```

4. Manager からのフィードバックへの対応

   - PR に対して Manager からコメントや修正要求が入る可能性がある。
   - Architect は、再度呼び出された場合:
     - PR コメントを読み、指摘内容を要約する。
     - 必要に応じてユーザーに追加ヒアリングを行い（1ターン1テーマ）、docs/ 以下のドキュメントを更新する。
     - `git add` / `git commit` / `git push` で既存 PR に差分を追加し、必要なら PR 上で修正内容を簡潔に説明する。
   - Manager が「問題なし」と判断するまで、このサイクルを繰り返す。