# Project Roadmap

## Project Summary
`prompt-improver` is a local-first CLI for evaluating whether a prompt should change, generating minimal improvements only when necessary, and supporting diff and test-oriented validation flows. The architecture keeps core logic separate from the CLI entry point so future local app interfaces can reuse the same domain behavior.

## Current Status
Current phase: `Phase 1: Setup`

The repository is establishing the Python 3.12, `uv`, `Typer`, `pytest`, `ruff`, and `mypy` foundation needed to implement the documented use cases with consistent local and CI execution paths.

## Phase Plan
### Phase 1: Setup
Establish the Python CLI project structure, quality gates, and CI workflow. Ensure the repository can install dependencies, run linting, execute tests, and expose a working `prompt-improver` entry point.

### Phase 2: UC_IMPROVE_PROMPT
Implement the main improvement workflow that judges a prompt, preserves intent, and returns a minimally edited improved prompt only when needed. Keep output aligned with the requirement that no unnecessary diff is produced for no-change cases.

### Phase 3: UC_JUDGE_PROMPT
Implement a fast judgment-only command that reports whether a prompt should change and why. This phase focuses on reliable reasoning output without requiring improved prompt generation.

### Phase 4: UC_REVIEW_DIFF
Add a diff review flow so users can inspect what changed between the original prompt and the improved prompt. Support clear change inspection that helps users validate the materiality of each edit.

### Phase 5: UC_RUN_TEST_CASES
Implement test case execution for prompt improvement scenarios, including per-case reporting and quality-oriented validation. This phase enables repeatable behavioral checks against curated local test inputs.

### Phase 6: UC_RUN_REGRESSION
Implement regression suite execution against stored expectations or snapshots to detect quality degradation over time. This phase protects existing behavior when core logic or prompt definitions evolve.

## Backlog / Future
- Add richer CLI subcommands and structured input/output file handling for all public operations in `docs/REQUIREMENT.md`.
- Introduce persistent local artifacts for reports, snapshots, metrics, and reusable test case management.
- Prepare a reusable application service layer that can back a future local app UI without duplicating domain logic.