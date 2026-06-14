import pytest
import sys

from pca.runtime.shell_runtime import run_command as runtime_run_command
from pca.tools.shell_tools import ShellCommandTool, run_command
from pca.tools.registry import ToolRegistry


def python_command(code: str) -> str:
    """使用当前测试进程的 Python 解释器执行一段内联代码。"""
    escaped_code = code.replace('"', '\\"')
    return f'"{sys.executable}" -c "{escaped_code}"'


class TestShellRuntime:
    """测试 shell 运行时功能"""

    def test_successful_command(self):
        """测试成功命令：运行一个简单 Python 命令，断言 returncode == 0，stdout 包含预期文本"""
        tool = ShellCommandTool()
        arguments = {
            "command": python_command("print('Hello, World!')"),
            "cwd": ".",
            "workspace_root": ".",
            "timeout_seconds": 5
        }

        result = tool.run(arguments)

        assert result["returncode"] == 0
        assert "Hello, World!" in result["stdout"]
        assert result["stderr"] == ""
        assert result["timed_out"] is False

    def test_failed_command(self):
        """测试失败命令：运行一个退出码非 0 的命令，断言 returncode != 0，并保留 stderr 或失败信息"""
        tool = ShellCommandTool()
        arguments = {
            "command": python_command("import sys; sys.exit(1)"),
            "cwd": ".",
            "workspace_root": ".",
            "timeout_seconds": 5
        }

        result = tool.run(arguments)

        assert result["returncode"] != 0
        assert result["returncode"] == 1
        # 注意：python 退出时 stderr 通常是空的，除非有错误信息

    def test_working_directory(self, tmp_path):
        """测试工作目录：在 tmp_path 下执行命令，断言命令看到的是指定 cwd"""
        tool = ShellCommandTool()

        # 创建测试文件
        test_file = tmp_path / "test_cwd.txt"
        test_file.write_text("cwd_test")

        # 使用命令检查当前目录
        arguments = {
            "command": python_command("import os; print(os.getcwd())"),
            "cwd": str(tmp_path),
            "workspace_root": str(tmp_path.parent),
            "timeout_seconds": 5
        }

        result = tool.run(arguments)

        assert result["returncode"] == 0
        # 输出的当前目录应该包含 tmp_path
        assert str(tmp_path) in result["stdout"].strip()

    def test_command_timeout(self):
        """测试超时：运行会 sleep 的命令，设置很短 timeout，断言 timed_out is True"""
        tool = ShellCommandTool()

        # 这个命令会 sleep 10 秒，但超时设置为 0.1 秒
        arguments = {
            "command": python_command("import time; time.sleep(10)"),
            "cwd": ".",
            "workspace_root": ".",
            "timeout_seconds": 0.1  # 很短的超时
        }

        result = tool.run(arguments)

        assert result["timed_out"] is True
        # 超时后应该没有正常输出
        assert result["stdout"] == ""
        assert result["returncode"] == -1  # 超时返回码

    def test_workspace_boundary_violation(self, tmp_path):
        """测试工作区边界：cwd 指向 workspace_root 外部时，抛 ValueError"""
        tool = ShellCommandTool()
        outside_dir = tmp_path.parent

        arguments = {
            "command": "echo test",
            "cwd": str(outside_dir),
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5
        }

        with pytest.raises(ValueError, match="outside workspace"):
            tool.run(arguments)

    def test_workspace_root_must_exist_and_be_directory(self, tmp_path):
        """测试 workspace_root 必须是已存在的目录。"""
        tool = ShellCommandTool()
        missing_root = tmp_path / "missing"
        file_root = tmp_path / "file.txt"
        file_root.write_text("not a directory", encoding="utf-8")

        for invalid_root in (missing_root, file_root):
            with pytest.raises(ValueError, match="workspace_root"):
                tool.run({
                    "command": "echo test",
                    "cwd": ".",
                    "workspace_root": str(invalid_root),
                    "timeout_seconds": 5,
                })

    def test_cwd_must_exist_and_be_directory(self, tmp_path):
        """测试 cwd 必须是工作区内已存在的目录。"""
        tool = ShellCommandTool()
        missing_cwd = tmp_path / "missing"
        file_cwd = tmp_path / "file.txt"
        file_cwd.write_text("not a directory", encoding="utf-8")

        for invalid_cwd in (missing_cwd, file_cwd):
            with pytest.raises(ValueError, match="cwd"):
                tool.run({
                    "command": "echo test",
                    "cwd": str(invalid_cwd),
                    "workspace_root": str(tmp_path),
                    "timeout_seconds": 5,
                })

    def test_tool_registry_integration(self):
        """测试 ToolRegistry 集成：把 run_command 注册成 Tool，通过 registry.run(...) 执行"""
        # 创建工具注册表
        registry = ToolRegistry()

        # 创建并注册工具
        tool = ShellCommandTool()
        registry.register(tool)

        # 准备参数
        arguments = {
            "command": python_command("print('ToolRegistry test')"),
            "cwd": ".",
            "workspace_root": ".",
            "timeout_seconds": 5
        }

        # 通过注册表执行
        result = registry.run("run_command", arguments)

        assert result["returncode"] == 0
        assert "ToolRegistry test" in result["stdout"]

    def test_command_with_environment_variables(self, tmp_path):
        """测试环境变量传递"""
        tool = ShellCommandTool()

        arguments = {
            "command": python_command("import os; print(os.environ.get('TEST_VAR', 'NOT_SET'))"),
            "cwd": str(tmp_path),
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5,
            "env": {"TEST_VAR": "TEST_VALUE"}
        }

        result = tool.run(arguments)

        assert result["returncode"] == 0
        assert "TEST_VALUE" in result["stdout"]

    def test_command_output_capture(self):
        """测试 stdout 和 stderr 的正确捕获"""
        tool = ShellCommandTool()

        # 这个命令会同时输出到 stdout 和 stderr
        arguments = {
            "command": python_command(
                "import sys; print('stdout message'); print('stderr message', file=sys.stderr)"
            ),
            "cwd": ".",
            "workspace_root": ".",
            "timeout_seconds": 5
        }

        result = tool.run(arguments)

        assert result["returncode"] == 0
        assert "stdout message" in result["stdout"]
        assert "stderr message" in result["stderr"]

    def test_command_accepts_argument_list(self, tmp_path):
        """测试 command 支持官方推荐的参数列表形式。"""
        result = runtime_run_command(
            {
                "command": [sys.executable, "-c", "print('list command')"],
                "cwd": ".",
                "workspace_root": str(tmp_path),
                "timeout_seconds": 5,
            }
        )

        assert result["returncode"] == 0
        assert result["stdout"].strip() == "list command"
        assert result["timed_out"] is False

    def test_command_list_preserves_arguments_with_spaces(self, tmp_path):
        """测试列表命令不用 shell 引号也能保留带空格的参数。"""
        result = runtime_run_command(
            {
                "command": [
                    sys.executable,
                    "-c",
                    "import sys; print(sys.argv[1])",
                    "value with spaces",
                ],
                "cwd": ".",
                "workspace_root": str(tmp_path),
                "timeout_seconds": 5,
            }
        )

        assert result["returncode"] == 0
        assert result["stdout"].strip() == "value with spaces"

    def test_command_list_rejects_invalid_items(self, tmp_path):
        """测试列表命令必须是非空字符串列表。"""
        invalid_commands = [
            [],
            [""],
            [" "],
            [sys.executable, None],
            [sys.executable, 123],
        ]

        for command in invalid_commands:
            with pytest.raises(ValueError, match="command"):
                runtime_run_command(
                    {
                        "command": command,
                        "cwd": ".",
                        "workspace_root": str(tmp_path),
                        "timeout_seconds": 5,
                    }
                )

    def test_backward_compatibility_function(self):
        """测试向后兼容的函数形式"""
        arguments = {
            "command": python_command("print('Backward compatibility test')"),
            "cwd": ".",
            "workspace_root": ".",
            "timeout_seconds": 5
        }

        result = run_command(arguments)

        assert result["returncode"] == 0
        assert "Backward compatibility test" in result["stdout"]

    def test_runtime_module_executes_command(self, tmp_path):
        """测试 runtime 层本身能执行命令，tool 层不应该独占 subprocess 逻辑。"""
        result = runtime_run_command(
            {
                "command": python_command("print('runtime layer')"),
                "cwd": ".",
                "workspace_root": str(tmp_path),
                "timeout_seconds": 5,
            }
        )

        assert result["returncode"] == 0
        assert result["stdout"].strip() == "runtime layer"

    def test_timeout_seconds_string_is_normalized(self, tmp_path):
        """测试 timeout_seconds 字符串会被规范化为数字再传给 subprocess。"""
        result = runtime_run_command(
            {
                "command": "echo timeout-string",
                "cwd": ".",
                "workspace_root": str(tmp_path),
                "timeout_seconds": "5",
            }
        )

        assert result["returncode"] == 0
        assert "timeout-string" in result["stdout"]
        assert result["timed_out"] is False

    def test_invalid_timeout_seconds_raises_value_error(self, tmp_path):
        """测试非法 timeout_seconds 在参数边界直接报错，而不是伪装成命令失败。"""
        with pytest.raises(ValueError, match="timeout_seconds"):
            runtime_run_command(
                {
                    "command": "echo invalid-timeout",
                    "cwd": ".",
                    "workspace_root": str(tmp_path),
                    "timeout_seconds": "not-a-number",
                }
            )

    def test_timeout_seconds_has_upper_bound(self, tmp_path):
        """测试超时时间必须有上限，避免 Agent 请求无限长执行。"""
        with pytest.raises(ValueError, match="timeout_seconds"):
            runtime_run_command(
                {
                    "command": "echo too-long",
                    "cwd": ".",
                    "workspace_root": str(tmp_path),
                    "timeout_seconds": 999999,
                }
            )

    def test_env_rejects_blank_keys(self, tmp_path):
        """测试环境变量 key 不能为空。"""
        with pytest.raises(ValueError, match="env"):
            runtime_run_command(
                {
                    "command": "echo env",
                    "cwd": ".",
                    "workspace_root": str(tmp_path),
                    "timeout_seconds": 5,
                    "env": {"": "VALUE"},
                }
            )

    def test_sensitive_env_values_are_redacted_from_output(self, tmp_path):
        """测试敏感环境变量值不会从命令输出中泄漏。"""
        secret_value = "sk-test-secret-value"

        result = runtime_run_command(
            {
                "command": [
                    sys.executable,
                    "-c",
                    "import os; print(os.environ['OPENAI_API_KEY'])",
                ],
                "cwd": ".",
                "workspace_root": str(tmp_path),
                "timeout_seconds": 5,
                "env": {"OPENAI_API_KEY": secret_value},
            }
        )

        assert result["returncode"] == 0
        assert secret_value not in result["stdout"]
        assert "[REDACTED]" in result["stdout"]

    def test_missing_required_arguments(self):
        """测试缺少必需参数"""
        tool = ShellCommandTool()

        # 缺少 command
        with pytest.raises(ValueError, match="Missing required argument"):
            tool.run({
                "workspace_root": ".",
                "timeout_seconds": 5
            })

        # 缺少 workspace_root
        with pytest.raises(ValueError, match="Missing required argument"):
            tool.run({
                "command": "echo test",
                "timeout_seconds": 5
            })

        # 缺少 timeout_seconds
        with pytest.raises(ValueError, match="Missing required argument"):
            tool.run({
                "command": "echo test",
                "workspace_root": "."
            })

    def test_relative_path_workspace_check(self):
        """测试相对路径的工作区检查"""
        tool = ShellCommandTool()

        # 使用相对路径
        arguments = {
            "command": "echo test",
            "cwd": ".",
            "workspace_root": "..",  # 父目录作为工作区根目录
            "timeout_seconds": 5
        }

        # 这应该成功，因为当前目录在父目录内
        result = tool.run(arguments)
        assert result["returncode"] == 0

    def test_command_with_special_characters(self):
        """测试包含特殊字符的命令"""
        tool = ShellCommandTool()

        arguments = {
            "command": "echo 'Hello, World! $PATH'",
            "cwd": ".",
            "workspace_root": ".",
            "timeout_seconds": 5
        }

        result = tool.run(arguments)

        assert result["returncode"] == 0
        assert "Hello, World!" in result["stdout"]


# 测试工具注册表的其他功能
class TestToolRegistryIntegration:
    """测试工具注册表集成"""

    def test_tool_registration_and_lookup(self):
        """测试工具注册和查找"""
        registry = ToolRegistry()
        tool = ShellCommandTool()

        # 注册工具
        registry.register(tool)

        # 检查工具是否存在
        assert registry.exists("run_command")
        assert "run_command" in registry.list_tools()

        # 获取工具
        retrieved_tool = registry.get("run_command")
        assert retrieved_tool.name == "run_command"

        # 测试重复注册
        with pytest.raises(KeyError, match="Duplicate tool"):
            registry.register(tool)

        # 测试未知工具
        with pytest.raises(KeyError, match="Unknown tool"):
            registry.get("unknown_tool")

    def test_tool_unregister(self):
        """测试工具注销"""
        registry = ToolRegistry()
        tool = ShellCommandTool()

        registry.register(tool)
        assert registry.exists("run_command")

        registry.unregister("run_command")
        assert not registry.exists("run_command")

        # 测试注销未知工具
        with pytest.raises(KeyError, match="Unknown tool"):
            registry.unregister("run_command")
