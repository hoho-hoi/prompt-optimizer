from pathlib import Path


def load_readme_text() -> str:
    readme_file_path = Path(__file__).resolve().parent.parent / "README.md"
    return readme_file_path.read_text(encoding="utf-8")


def test_readme_explains_product_principle() -> None:
    readme_text = load_readme_text()

    assert "必要なら直し、不要なら直さない" in readme_text
    assert "prompt improver" in readme_text.lower()


def test_readme_includes_short_setup_path_and_required_environment_variables() -> None:
    readme_text = load_readme_text()

    assert "Python 3.12" in readme_text
    assert "`uv`" in readme_text
    assert "`make setup`" in readme_text
    assert "OPENAI_COMPATIBLE_BASE_URL" in readme_text
    assert "OPENAI_COMPATIBLE_API_KEY" in readme_text
    assert "PROMPT_IMPROVER_MODEL_NAME" in readme_text
    assert "prompt-improver improve" in readme_text


def test_readme_documents_file_input_and_standard_input_examples() -> None:
    readme_text = load_readme_text()

    assert "--input" in readme_text
    assert "standard input" in readme_text.lower()
    assert "originalPrompt" in readme_text
    assert "improvementRequests" in readme_text


def test_readme_explains_improve_output_fields() -> None:
    readme_text = load_readme_text()

    assert "`judgment`" in readme_text
    assert "`reason`" in readme_text
    assert "`improved_prompt`" in readme_text
    assert "`changes`" in readme_text


def test_readme_marks_unimplemented_public_commands() -> None:
    readme_text = load_readme_text()

    assert "`judge`" in readme_text
    assert "`diff`" in readme_text
    assert "`test`" in readme_text
    assert "`regression`" in readme_text
    assert "未実装" in readme_text or "今後の予定" in readme_text
