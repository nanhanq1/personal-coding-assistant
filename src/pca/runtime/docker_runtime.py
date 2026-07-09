"""Docker sandbox runtime 的最小 adapter。"""

from __future__ import annotations

import subprocess
import shutil
import time
from pathlib import Path
from typing import Any

from pca.runtime.shell_runtime import (
    DEFAULT_MAX_TIMEOUT_SECONDS,
    _coerce_output,
    _elapsed_ms,
    _normalize_command,
    _normalize_timeout,
    _redact_sensitive_values,
    _resolve_cwd,
    _resolve_workspace_root,
    _sensitive_env_values,
)


DOCKER_UNAVAILABLE_FALLBACK = "docker_unavailable"
DEFAULT_DOCKER_IMAGE = "python:3.11-slim"
DOCKER_DAEMON_CHECK_TIMEOUT_SECONDS = 5.0


class DockerRuntime:
    """通过 Docker 执行命令；Docker 不可用时返回稳定 fallback。"""

    def __init__(
        self,
        image: str = DEFAULT_DOCKER_IMAGE,
        max_timeout_seconds: float = DEFAULT_MAX_TIMEOUT_SECONDS,
    ) -> None:
        # 修改前旧代码：
        # """Docker sandbox runtime 占位模块，计划在本地 runtime 基础之后实现。"""
        #
        # 问题：模块只是占位，没有实现 CommandRuntime.run(arguments)，调用方无法
        # 判断 Docker 不可用时应如何失败，也容易误以为已经具备 sandbox 能力。
        if not isinstance(image, str) or image.strip() == "":
            raise ValueError("image must be a non-empty string")
        if max_timeout_seconds <= 0:
            raise ValueError("max_timeout_seconds must be greater than 0")
        self._image = image
        self._max_timeout_seconds = float(max_timeout_seconds)

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """执行 Docker 命令；不可用时不回退到宿主机 shell。"""
        command = _normalize_command(arguments)
        workspace_root = _resolve_workspace_root(arguments)
        timeout_seconds = _normalize_timeout(arguments, self._max_timeout_seconds)
        resolved_cwd = _resolve_cwd(arguments, workspace_root)
        sensitive_env_values = _sensitive_env_values(arguments.get("env"))
        started_at = time.monotonic()

        docker_executable = shutil.which("docker")
        if docker_executable is None:
            return _unavailable_result(
                "docker executable not found",
                127,
                started_at,
            )

        availability = _check_docker_available(docker_executable, started_at)
        if availability is not None:
            return availability

        docker_command = _build_docker_command(
            docker_executable=docker_executable,
            image=self._image,
            command=command,
            workspace_root=workspace_root,
            resolved_cwd=resolved_cwd,
            env=arguments.get("env"),
        )

        try:
            completed = subprocess.run(
                docker_command,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "stdout": _redact_sensitive_values(
                    _coerce_output(exc.stdout),
                    sensitive_env_values,
                ),
                "stderr": _redact_sensitive_values(
                    _coerce_output(exc.stderr)
                    or f"Docker command timed out after {timeout_seconds} seconds",
                    sensitive_env_values,
                ),
                "returncode": -1,
                "timed_out": True,
                "duration_ms": _elapsed_ms(started_at),
                "sandboxed": True,
                "fallback": None,
            }
        except FileNotFoundError:
            return _unavailable_result(
                "docker executable disappeared during execution",
                127,
                started_at,
            )

        return {
            "stdout": _redact_sensitive_values(completed.stdout, sensitive_env_values),
            "stderr": _redact_sensitive_values(completed.stderr, sensitive_env_values),
            "returncode": completed.returncode,
            "timed_out": False,
            "duration_ms": _elapsed_ms(started_at),
            "sandboxed": True,
            "fallback": None,
        }


def _check_docker_available(
    docker_executable: str,
    started_at: float,
) -> dict[str, Any] | None:
    """确认 Docker CLI 和 daemon 可用；失败时返回 graceful fallback。"""
    try:
        completed = subprocess.run(
            [docker_executable, "version", "--format", "{{.Server.Version}}"],
            capture_output=True,
            text=True,
            timeout=DOCKER_DAEMON_CHECK_TIMEOUT_SECONDS,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        return _unavailable_result("docker daemon check timed out", 125, started_at)
    except FileNotFoundError:
        return _unavailable_result("docker executable not found", 127, started_at)

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "docker daemon is not available").strip()
        return _unavailable_result(detail, 125, started_at)

    return None


def _build_docker_command(
    *,
    docker_executable: str,
    image: str,
    command: str | list[str],
    workspace_root: Path,
    resolved_cwd: Path,
    env: Any,
) -> list[str]:
    container_cwd = _container_cwd(workspace_root, resolved_cwd)
    docker_command = [
        docker_executable,
        "run",
        "--rm",
        "-v",
        f"{workspace_root}:/workspace",
        "-w",
        container_cwd,
    ]
    docker_command.extend(_docker_env_args(env))
    docker_command.append(image)

    if isinstance(command, str):
        docker_command.extend(["sh", "-lc", command])
    else:
        docker_command.extend(command)
    return docker_command


def _container_cwd(workspace_root: Path, resolved_cwd: Path) -> str:
    if resolved_cwd == workspace_root:
        return "/workspace"
    return "/workspace/" + resolved_cwd.relative_to(workspace_root).as_posix()


def _docker_env_args(env: Any) -> list[str]:
    if env is None:
        return []
    if not isinstance(env, dict):
        raise ValueError("env must be a dictionary")

    docker_args: list[str] = []
    for key, value in env.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("env keys and values must be strings")
        if key.strip() == "":
            raise ValueError("env keys must be non-empty strings")
        docker_args.extend(["-e", f"{key}={value}"])
    return docker_args


def _unavailable_result(
    reason: str,
    returncode: int,
    started_at: float,
) -> dict[str, Any]:
    return {
        "stdout": "",
        "stderr": f"Docker runtime unavailable: {reason}",
        "returncode": returncode,
        "timed_out": False,
        "duration_ms": _elapsed_ms(started_at),
        "sandboxed": False,
        "fallback": DOCKER_UNAVAILABLE_FALLBACK,
    }
