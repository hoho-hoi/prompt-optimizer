import importlib
import subprocess


def testImportPromptOptimizerPackage() -> None:
    imported_module = importlib.import_module("prompt_optimizer")

    assert imported_module is not None


def testRunPromptImproverHelpCommand() -> None:
    completed_process = subprocess.run(
        ["prompt-improver", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed_process.returncode == 0
    assert "Usage" in completed_process.stdout
