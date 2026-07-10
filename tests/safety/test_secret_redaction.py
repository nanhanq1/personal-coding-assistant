import sys
import uuid
from pathlib import Path

from pca.runtime.shell_runtime import ShellRuntime


def test_shell_runtime_redacts_sensitive_env_value_without_echoing_secret(
    tmp_path: Path,
) -> None:
    """本地命令输出敏感环境变量时，返回值必须只包含脱敏占位符。"""
    secret = "safety-" + uuid.uuid4().hex
    result = ShellRuntime().run(
        {
            "command": [
                sys.executable,
                "-c",
                "import os; print(os.environ['PCA_TEST_API_TOKEN'])",
            ],
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5,
            "env": {"PCA_TEST_API_TOKEN": secret},
        },
    )

    if result["stdout"] != "[REDACTED]\n":
        raise AssertionError("shell runtime did not redact sensitive environment output")
    if secret in result["stderr"]:
        raise AssertionError("shell runtime returned a sensitive value in stderr")
