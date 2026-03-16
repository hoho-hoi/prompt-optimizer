# Project Requirements

<!--
このファイルはプロジェクトの要件定義のメインエントリです。
Goal / Domain / Interaction / Architecture の4本柱をまとめて記述します。

他の設計ファイルとの関係:
- ドメイン構造: DOMAIN_ER.md
- インタラクション状態遷移: INTERACTION_FLOW.md
- コンポーネント構成: ARCHITECTURE_DIAGRAM.md
- ユースケース詳細: USE_CASES.md

運用ルール:
- 「TBD」や空欄のままにせず、すべての項目に具体的な内容を埋めてから次フェーズに進むこと。
- 説明文は必要に応じて削除してよいが、見出し・項目名は原則残すこと。
-->

---

## 1. Overview (Goal / Scope)

### 1.1 Product Summary

<!-- プロジェクトの概要を短く定義する。 -->

- Goal:  
- Target Users:  
- One-line Description:  

### 1.2 Scope

<!--
スコープ内とスコープ外を明確に切り分ける。
「やらないこと」を書くことでスコープの暴走を防ぐ。
-->

- In Scope:  
- Out of Scope:  

### 1.3 Success Criteria & Constraints

<!--
成功判定の基準と、守るべき制約条件を記述する。
例: 指標(DAU, 継続率, 応答時間)や締切、対応プラットフォームなど。
-->

- Success Criteria:  
- Constraints:  

---

## 2. Domain Model (Domain)

### 2.1 Domain Entities

<!--
ドメインエンティティとその関係は DOMAIN_ER.md に mermaid の erDiagram 形式で記述する。

DOMAIN_ER.md では、各エンティティに storage_scope をコメントで付与する運用を想定する:
- Ephemeral          : 1操作 / 1フレーム内だけで完結する一時データ
- Session            : セッション(ログイン中, ゲーム1プレイ中 等)の間維持されるデータ
- DeviceLocal        : デバイス上に永続化され、主にそのデバイスだけで利用されるデータ
- UserPersistent     : ユーザアカウントに紐づき、複数デバイス間で共有されるデータ
- GlobalPersistent   : システム全体で共有される永続データ
-->

- Domain ER Diagram: see `DOMAIN_ER.md`  

### 2.2 Domain Notes (Optional)

<!--
ER 図だけでは表現しづらいルールや補足がある場合に記述する。
何もなければ空でもよい。
-->

- Notes:  

---

## 3. Interaction / UI / Operations

### 3.1 Interaction State Flow

<!--
システム全体のインタラクション状態遷移は INTERACTION_FLOW.md に mermaid flowchart で記述する。

ルール:
- ノードIDは状態(State)IDとして扱う（例: STATE_TITLE, STATE_IN_GAME 等）。
- 矢印には可能な限り「イベント名」をラベルとして付ける。
  例: |start_button_clicked|, |timer_expired|, |message_received| など。
-->

- Interaction State Diagram: see `INTERACTION_FLOW.md`  

### 3.2 Public Operations / APIs

<!--
クライアント(人間・他システム・外部アプリ等)から見える操作/インターフェースを列挙する。
Web の場合は HTTP パス、CLI の場合はコマンド、ゲーム/組み込みの場合は公開APIやメッセージ名など。

列挙した OP_ID は USE_CASES.md の Operations から参照される前提。
-->

| OP_ID | Interface / Path / Command | Summary |
|-------|----------------------------|---------|
|       |                            |         |
|       |                            |         |

### 3.3 Use Cases

<!--
ユースケースの詳細仕様は USE_CASES.md に記述する。

ここでは「ユースケースの一覧」や「重要なユースケースIDだけ」を簡潔に列挙しておくとよい。
-->

- Key Use Case IDs:  

---

## 4. Architecture

### 4.1 Components & Data Flow

<!--
システムを構成する主要なコンポーネント(箱)とデータフローは ARCHITECTURE_DIAGRAM.md に mermaid flowchart で記述する。

ルール:
- ノードはコンポーネント(例: Frontend, API Server, GameServer, DeviceController 等)。
- 外部サービス・外部デバイスはノード名に「(外部)」を付ける。
- 矢印には可能な限り「代表的な操作/プロトコル名」をラベルとして付ける。
  例: |HTTP /api/login|, |gRPC Match|, |I2C Read| など。
-->

- Architecture Diagram: see `ARCHITECTURE_DIAGRAM.md`  

### 4.2 Storage Scope Policy

<!--
DOMAIN_ER.md で付与した storage_scope を、具体的なストレージ/媒体にマッピングする方針を記述する。
例: UserPersistent -> クラウドDB, Session -> サーバメモリ+キャッシュ 等。
-->

- Ephemeral:  
- Session:  
- DeviceLocal:  
- UserPersistent:  
- GlobalPersistent:  

### 4.3 Non-Functional Requirements (Architecture-related)

<!--
アーキテクチャ設計に強く影響する非機能要件のみを記述する。
詳細なSLAや細かい数値要件がある場合は別ドキュメントに分けてもよい。
-->

- Performance / Throughput:  
- Security / Authentication / Authorization:  
- Availability / Reliability / Backup:  
- Observability (Logging / Metrics / Tracing / Alerting):  
- Other NFRs:  