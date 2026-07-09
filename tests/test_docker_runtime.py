import sys
from importlib import import_module

from pca.runtime.interface import CommandRuntime


def _docker_runtime_type() -> type:
    module = import_module("pca.runtime.docker_runtime")
    return module.DockerRuntime


def test_docker_runtime_satisfies_command_runtime_protocol() -> None:
    """DockerRuntime 应实现 CommandRuntime 的最小 run(arguments) 接口。"""
    DockerRuntime = _docker_runtime_type()

    assert isinstance(DockerRuntime(), CommandRuntime)


def test_docker_runtime_returns_graceful_fallback_when_cli_missing(
    monkeypatch,
    tmp_path,
) -> None:
    """Docker CLI 缺失时应返回稳定失败结果，而不是抛平台相关异常。"""
    DockerRuntime = _docker_runtime_type()
    monkeypatch.setattr("pca.runtime.docker_runtime.shutil.which", lambda name: None)

    result = DockerRuntime().run(
        {
            "command": "echo should-not-run",
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5,
        }
    )

    assert result == {
        "stdout": "",
        "stderr": "Docker runtime unavailable: docker executable not found",
        "returncode": 127,
        "timed_out": False,
        "duration_ms": result["duration_ms"],
        "sandboxed": False,
        "fallback": "docker_unavailable",
    }
    assert isinstance(result["duration_ms"], int)


def test_docker_runtime_does_not_fall_back_to_host_shell_when_unavailable(
    monkeypatch,
    tmp_path,
) -> None:
    """Docker 不可用时不能静默改用宿主机 shell 执行。"""
    DockerRuntime = _docker_runtime_type()
    monkeypatch.setattr("pca.runtime.docker_runtime.shutil.which", lambda name: None)
    marker = tmp_path / "host-executed.txt"

    result = DockerRuntime().run(
        {
            "command": [
                sys.executable,
                "-c",
                "from pathlib import Path; Path('host-executed.txt').write_text('bad')",
            ],
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5,
        }
    )

    assert result["fallback"] == "docker_unavailable"
    assert result["sandboxed"] is False
    assert not marker.exists()


def test_docker_runtime_returns_graceful_fallback_when_daemon_unavailable(
    monkeypatch,
    tmp_path,
) -> None:
    """Docker daemon 不可用时应清晰失败，而不是继续执行用户命令。"""
    DockerRuntime = _docker_runtime_type()
    calls: list[list[str]] = []

    class Completed:
        returncode = 1
        stdout = ""
        stderr = "Cannot connect to the Docker daemon"

    def fake_run(command, **kwargs):
        calls.append(command)
        return Completed()

    monkeypatch.setattr("pca.runtime.docker_runtime.shutil.which", lambda name: "docker")
    monkeypatch.setattr("pca.runtime.docker_runtime.subprocess.run", fake_run)

    result = DockerRuntime().run(
        {
            "command": "echo should-not-run",
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5,
        }
    )

    assert result["returncode"] == 125
    assert result["fallback"] == "docker_unavailable"
    assert result["sandboxed"] is False
    assert "Cannot connect to the Docker daemon" in result["stderr"]
    assert calls == [["docker", "version", "--format", "{{.Server.Version}}"]]
