---  # .github/ISSUE_TEMPLATE/setup.md
name: Setup Task
about: 開発環境・ツール・CI・ROADMAP などの初期セットアップ用タスク
title: "[SETUP] "
labels: setup
assignees: ''
---

## 目的（何をセットアップするか）

<!-- Manager が記入する。例:
- 選定した技術スタック（言語・フレームワーク）に基づき、開発環境を整える
- テスト・Lint・Format ツールチェーンを導入し、Makefile から実行できるようにする
- CI で `make test` / `make lint` が実行される状態にする
- ROADMAP.md を初期化し、今後のフェーズ構成を見える化する
-->

## 作業内容（Engineer はこの指示をベースに実装する）

<!--
  Manager が「どう編集してほしいか」をできるだけ具体的に書く。
  特に docs 系（ROADMAP.md など）の変更については、
  構成や項目をかなり厳密に指定することを推奨する。
  ツール設定（Makefile / CI / Lint / Format / テスト設定）については、
  使用するツール名や実行コマンド方針を明示し、細部は Engineer にある程度任せてもよい。
-->

- Makefile:
  - 例: `setup`, `test`, `lint`, `format` などのターゲットを定義する
- Lint / Format / Test:
  - 使用するツール（例: ESLint / Prettier / Vitest / pytest / ruff など）と設定ファイルの方針を書く
- CI:
  - どのイベント（push / pull_request など）で、どのコマンド（`make test` / `make lint` …）を実行するかを書く
- ROADMAP.md（初期化する場合）:
  - 例: 「プロジェクト概要」「フェーズ一覧（Setup / UC1 / UC2 …）」「各フェーズのゴール」を作成する など

## Acceptance Criteria（完了の定義）

<!-- 「このチェックがすべて満たされたら Done」と言える状態を厳密に書く -->

- [ ] `make setup` がローカルで成功する（定義している場合）
- [ ] `make test` がローカルで成功する
- [ ] `make lint` がローカルで成功する
- [ ] `make format` がローカルで成功する（定義している場合）
- [ ] GitHub Actions の CI で `make test` / `make lint` が成功している
- [ ] 上記「作業内容」に書かれた編集指示がすべて反映されている
- [ ] ROADMAP.md を初期化する場合、この Issue に書かれたアウトラインと内容が一致している
