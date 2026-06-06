import locale
import os
import subprocess
from pathlib import Path
from typing import Any


class ShellRuntime:
    """负责在受控工作目录中执行 shell 命令。"""

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """执行命令并返回 stdout、stderr、returncode 和 timed_out。"""
        command = _require_command(arguments)
        workspace_root = _resolve_workspace_root(arguments)
        timeout_seconds = _normalize_timeout(arguments)
        resolved_cwd = _resolve_cwd(arguments, workspace_root)
        full_env = _build_environment(arguments)
        output_encoding = locale.getpreferredencoding(False)

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=resolved_cwd,
                env=full_env,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                encoding=output_encoding,
                errors="replace",
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "stdout": _coerce_output(exc.stdout),
                "stderr": _coerce_output(exc.stderr)
                or f"Command timed out after {timeout_seconds} seconds",
                "returncode": -1,
                "timed_out": True,
            }

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "timed_out": False,
        }


def run_command(arguments: dict[str, Any]) -> dict[str, Any]:
    """函数形式入口，便于工具注册和单元测试直接调用。"""
    return ShellRuntime().run(arguments)


def _require_command(arguments: dict[str, Any]) -> str:
    if "command" not in arguments:
        raise ValueError("Missing required argument: command")

    command = arguments["command"]
    if not isinstance(command, str) or command.strip() == "":
        raise ValueError("command must be a non-empty string")
    return command


def _resolve_workspace_root(arguments: dict[str, Any]) -> Path:
    if "workspace_root" not in arguments:
        raise ValueError("Missing required argument: workspace_root")

    raw_workspace_root = arguments["workspace_root"]
    if raw_workspace_root is None or str(raw_workspace_root).strip() == "":
        raise ValueError("workspace_root must be a non-empty path")
    return Path(str(raw_workspace_root)).resolve()


def _normalize_timeout(arguments: dict[str, Any]) -> float:
    """把 timeout_seconds 规范化为 subprocess 可直接使用的正浮点数。"""
    if "timeout_seconds" not in arguments:
        raise ValueError("Missing required argument: timeout_seconds")

    raw_timeout = arguments["timeout_seconds"]
    try:
        timeout_seconds = float(raw_timeout)
    except (TypeError, ValueError) as exc:
        raise ValueError("timeout_seconds must be a number greater than 0") from exc

    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be a number greater than 0")
    return timeout_seconds


def _resolve_cwd(arguments: dict[str, Any], workspace_root: Path) -> Path:
    raw_cwd = arguments.get("cwd", ".")
    if raw_cwd is None or str(raw_cwd).strip() == "":
        raise ValueError("cwd must be a non-empty path")

    cwd_path = Path(str(raw_cwd))
    if cwd_path.is_absolute():
        resolved_cwd = cwd_path.resolve()
    else:
        resolved_cwd = (workspace_root / cwd_path).resolve()

    if resolved_cwd != workspace_root and workspace_root not in resolved_cwd.parents:
        raise ValueError(
            f"Working directory '{resolved_cwd}' is outside workspace root '{workspace_root}'"
        )
    return resolved_cwd


def _build_environment(arguments: dict[str, Any]) -> dict[str, str] | None:
    env = arguments.get("env")
    if env is None:
        return None
    if not isinstance(env, dict):
        raise ValueError("env must be a dictionary")

    full_env = os.environ.copy()
    for key, value in env.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("env keys and values must be strings")
        full_env[key] = value
    return full_env


def _coerce_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(locale.getpreferredencoding(False), errors="replace")
    return value
