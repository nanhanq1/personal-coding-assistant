import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pca.runtime.checkpoints import FileCheckpoint
from pca.runtime.workspace import Workspace


def _run_demo() -> dict[str, Any]:
    """展示本地 workspace 文件 checkpoint 和失败后的 rollback。"""
    with TemporaryDirectory() as workspace_root:
        workspace_path = Path(workspace_root)
        file_name = "demo.txt"
        target = workspace_path / file_name
        original_content = "stable workspace content\n"
        temporary_failed_content = "partial failed edit\n"

        target.write_text(original_content, encoding="utf-8")
        workspace = Workspace(workspace_path)
        checkpoint = FileCheckpoint.create(workspace, [file_name])

        simulated_error = ""
        try:
            target.write_text(temporary_failed_content, encoding="utf-8")
            raise RuntimeError("simulated failure after local file change")
        except RuntimeError as error:
            simulated_error = str(error)
            checkpoint.restore()

        content_after_rollback = target.read_text(encoding="utf-8")

    return {
        "file_name": file_name,
        "original_content": original_content,
        "temporary_failed_content": temporary_failed_content,
        "content_after_rollback": content_after_rollback,
        "restored": content_after_rollback == original_content,
        "simulated_error": simulated_error,
        "capability_boundary": {
            "workspace_file_state_restored": content_after_rollback == original_content,
            "network_or_api_side_effects_restored": False,
            "package_install_side_effects_restored": False,
            "background_processes_restored": False,
            "outside_workspace_side_effects_restored": False,
            "shell_or_docker_or_git_auto_rollback": False,
        },
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print(json.dumps(_run_demo(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
