# DOMAIN_ER.md

<!--
このファイルでは、ドメインエンティティとその関係を mermaid の erDiagram 形式で記述する。

目的:
- 「このシステムの世界には何が存在し、どう関係しているか」をユーザーと合意する。
- クラス図やテーブル定義など、後続の詳細設計のベースとする。

ルール:
- 永続/非永続に関わらず「ドメインとして意味のあるエンティティ」を列挙する。
- 各エンティティの属性コメントに storage_scope を付与する (任意だが推奨):

  storage_scope 候補:
    - Ephemeral        : 1操作 / 1フレーム内だけで完結
    - Session          : セッション(ログイン中, ゲーム1プレイ中 等)の間維持
    - DeviceLocal      : デバイスローカルに永続化
    - UserPersistent   : ユーザアカウントに紐づき複数デバイス間で共有
    - GlobalPersistent : システム全体で共有される永続データ

- 関係(1:1, 1:N, N:M等)には簡潔な説明ラベルを書くとよい。
-->

```mermaid
erDiagram
  %% ここにプロジェクト固有のドメインエンティティと関係を記述する
  %% 例:
  %% USER ||--o{ SCORE : "ユーザは複数のスコアを持つ (1:N)"
  %% USER {
  %%   string id    PK   "storage_scope: UserPersistent / UUID"
  %%   string name       "storage_scope: UserPersistent / 必須"
  %% }
  %% SCORE {
  %%   string id     PK   "storage_scope: UserPersistent"
  %%   string userId FK   "storage_scope: UserPersistent"
  %%   int    value       "0以上 / storage_scope: UserPersistent"
  %% }