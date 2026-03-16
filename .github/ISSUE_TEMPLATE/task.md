---
name: Implementation Task
about: 通常の実装タスク（テスト・Lint・CI を前提とした開発）
title: "[TASK] "
labels: task
assignees: ''
---

## 概要（このタスクの一言サマリ）

<!-- Manager が記入する。例:
- UC1 の「◯◯画面で△△操作ができるようにする」
- ドメインロジック X の実装とテスト追加
-->

- 

## Requirements (What needs to be done)

<!--
  実装すべき要件を R1, R2, ... の形で列挙する。
  Engineer は、PR の Self-Walkthrough とテストで各 Rn に対応する説明を書く前提で動く。
-->

- [ ] R1: Requirement 1
- [ ] R2: Requirement 2
- [ ] R3: Requirement 3 (必要なら追加)

## 実装の方針メモ（任意）

<!--
  Manager が「どう実装してほしいか」を補足したい場合に使う。
  - 触ってよいレイヤー / モジュール
  - 想定しているインターフェースや状態遷移
  などを簡潔に記載する。
-->

- 対象モジュール / コンポーネント:
- 想定する挙動・制約:

## Acceptance Criteria (Definition of Done)

<!--
  「Done と見なす条件」を書く。
  特に最初の項目で「各要件 R1, R2, ... が Self-Walkthrough とテストで対応付けられていること」を明示する。
-->

- [ ] 各要件（R1, R2, ...）が PR の Self-Walkthrough で明示的に参照されている  
      （例: 「R1: ◯◯ → 対応コード: ..., テスト: ...」のように対応関係が書かれている）
- [ ] 各要件（R1, R2, ...）が少なくとも 1 つ以上の自動テスト（ユニット / コンポーネントなど）で検証されている
- [ ] `make test` がローカルで成功する
- [ ] `make lint` がローカルで成功する
- [ ] （定義されている場合）`make format` 実行後も `make lint` / `make test` が成功している
