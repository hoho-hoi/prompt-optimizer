# DOMAIN_ER.md

```mermaid
erDiagram
  IMPROVE_REQUEST ||--|| IMPROVE_RESULT : produces
  IMPROVE_RESULT ||--o| DIFF_ARTIFACT : exposes
  IMPROVE_RESULT ||--o| METRICS_SNAPSHOT : includes
  TEST_SUITE ||--o{ TEST_CASE : groups
  TEST_CASE ||--o{ TEST_CASE_RESULT : evaluated_as
  TEST_RUN ||--o{ TEST_CASE_RESULT : records
  TEST_RUN }o--|| TEST_SUITE : targets
  EXECUTION_CONFIGURATION ||--o{ TEST_RUN : applies_to
  APPLICATION_SETTING ||--|| EXECUTION_CONFIGURATION : provides_default
  PROMPT_MODULE ||--o{ TEST_RUN : validated_by

  IMPROVE_REQUEST {
    string requestId PK "storage_scope: Session / one execution unit"
    text originalPrompt "required / storage_scope: Session"
    text improvementRequests "optional reference only / storage_scope: Session"
    text ioExamples "optional / storage_scope: Session"
    text additionalConstraints "optional / storage_scope: Session"
    string context "optional / storage_scope: Session"
  }

  IMPROVE_RESULT {
    string resultId PK "storage_scope: DeviceLocal / persisted result"
    string judgment "改善不要|改善推奨|改善必須"
    text reason "storage_scope: DeviceLocal"
    text improvedPrompt "storage_scope: DeviceLocal"
    text changes "storage_scope: DeviceLocal / summary list or none"
  }

  DIFF_ARTIFACT {
    string diffId PK "storage_scope: DeviceLocal"
    string format "unified|side_by_side|summary"
    text content "storage_scope: DeviceLocal"
  }

  METRICS_SNAPSHOT {
    string metricsId PK "storage_scope: DeviceLocal"
    int originalLength "storage_scope: DeviceLocal"
    int improvedLength "storage_scope: DeviceLocal"
    float compressionRatio "optional / storage_scope: DeviceLocal"
    int editDistance "optional / storage_scope: DeviceLocal"
    float redundancyScore "optional / storage_scope: DeviceLocal"
  }

  TEST_SUITE {
    string suiteId PK "storage_scope: DeviceLocal"
    string name "default or custom suite"
    string purpose "manual|regression"
  }

  TEST_CASE {
    string caseId PK "storage_scope: DeviceLocal"
    string category "改善不要|改善必須|相反要求 etc."
    text inputPayload "serialized ImproveRequest"
    text expectedBehavior "judgment and behavioral expectations"
    text rubricRule "optional scoring constraints"
  }

  TEST_RUN {
    string runId PK "storage_scope: DeviceLocal"
    string mode "test|regression"
    datetime startedAt "storage_scope: DeviceLocal"
    string reportFormat "text|json|markdown|html"
    string status "running|passed|failed"
  }

  TEST_CASE_RESULT {
    string caseResultId PK "storage_scope: DeviceLocal"
    int totalScore "0-10"
    text failureTags "over_editing etc."
    string verdict "passed|failed"
  }

  EXECUTION_CONFIGURATION {
    string configurationId PK "storage_scope: DeviceLocal"
    string modelName "optional selected model"
    boolean allowNoChange "storage_scope: DeviceLocal"
    boolean strictMinimalEdit "storage_scope: DeviceLocal"
    boolean preferShort "storage_scope: DeviceLocal"
    string outputFormat "text|json|markdown"
  }

  APPLICATION_SETTING {
    string settingId PK "storage_scope: DeviceLocal"
    string outputLanguage "example: Japanese"
    string concisenessPriority "user-selected priority"
    string minimalEditStrength "user-selected strength"
    string apiSettingRef "env or local config reference"
  }

  PROMPT_MODULE {
    string moduleId PK "storage_scope: DeviceLocal"
    string moduleType "system|evaluation|formatting|test_judge"
    text promptBody "replaceable prompt definition"
  }
```

- `IMPROVE_REQUEST` は単発実行の入力単位であり、必須入力は `originalPrompt` のみとする。
- `IMPROVE_RESULT` は判定と改善後プロンプトの一貫性を持つ成果物である。
- `TEST_CASE` は完全一致ではなく、期待挙動とルーブリック制約を保持する。
- `PROMPT_MODULE` は将来的な prompt definition 差し替えを可能にするための構成要素である。