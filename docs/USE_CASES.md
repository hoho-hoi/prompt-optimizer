# USE_CASES.md

<!--
このファイルでは、ユースケース仕様をテキストで記述する。
UMLの Fully Dressed Use Case を簡略化し、Domain / State / Operations と
トレースしやすい構造にしている。

関係:
- States: INTERACTION_FLOW.md の状態IDを参照する。
- Operations: REQUIREMENT.md の Public Operations / APIs の OP_ID を参照する。
- Domain: DOMAIN_ER.md のエンティティ・ルールと整合している必要がある。

ルール:
- 各ユースケースは UC-ID 単位で 1 ブロックとして記述する。
- Precondition / Postcondition はできる限り Domain の用語で書く。
- States / Operations は配列のように [] 内にIDを列挙する。
- ErrorCases は代表的なものだけでよいが、「どう扱うか」も簡潔に書くこと。
-->

## Use Cases

### UC-1

<!--
例:
- UC_ID        : UC_UPDATE_PROFILE
- Title        : プロフィール編集
- Actor        : 一般ユーザ
-->

- UC_ID:  
- Title:  
- Actor:  

- Goal:  

- Precondition:  
- Postcondition:  

- States: [  ]  
  <!-- INTERACTION_FLOW.md の状態ID列。例: [STATE_HOME -> STATE_PROFILE_EDIT -> STATE_PROFILE_VIEW] -->

- Operations: [  ]  
  <!-- REQUIREMENT.md の OP_ID や主要な操作名を列挙する。 -->

- ErrorCases:
  -  

---

### UC-2

- UC_ID:  
- Title:  
- Actor:  

- Goal:  

- Precondition:  
- Postcondition:  

- States: [  ]  

- Operations: [  ]  

- ErrorCases:
  -  

<!--
UC-3 以降も同じテンプレートをコピーして必要なだけ追加する。
-->