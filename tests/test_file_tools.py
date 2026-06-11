from pathlib import Path

import pytest
from pca.tools import create_coding_tool_registry
import pca.tools.file_tools as file_tools
from pca.tools.file_tools import ReadFileTool, WriteFileTool, read_file, write_file
from pca.tools.registry import ToolRegistry


class TestReadFileTool:
    """测试 ReadFileTool 类"""

    def test_returns_content(self, tmp_path):
        """测试读取文件返回正确内容"""
        tool = ReadFileTool()
        test_file = tmp_path / "test.txt"
        expected_content = "Hello, World!"
        test_file.write_text(expected_content, encoding="utf-8")

        result = tool.run({"path": "test.txt", "workspace_root": str(tmp_path)})

        assert result == expected_content

    def test_raises_when_file_missing(self, tmp_path):
        """测试文件不存在时抛出 FileNotFoundError"""
        tool = ReadFileTool()

        with pytest.raises(FileNotFoundError):
            tool.run({"path": "missing.txt", "workspace_root": str(tmp_path)})

    def test_rejects_directory_path(self, tmp_path):
        """测试读取目录时抛出清晰错误，而不是依赖系统 PermissionError。"""
        tool = ReadFileTool()
        directory = tmp_path / "folder"
        directory.mkdir()

        with pytest.raises(IsADirectoryError, match="path is a directory"):
            tool.run({"path": "folder", "workspace_root": str(tmp_path)})

    def test_rejects_blank_path(self, tmp_path):
        """测试空路径会被拒绝"""
        tool = ReadFileTool()

        for invalid_path in ("", " ", None):
            with pytest.raises(ValueError, match="path"):
                tool.run({"path": invalid_path, "workspace_root": str(tmp_path)})

    def test_rejects_non_string_path(self, tmp_path):
        """测试 path 必须是字符串，避免把 LLM 坏参数静默转成文件名。"""
        tool = ReadFileTool()

        with pytest.raises(TypeError, match="path"):
            tool.run({"path": 123, "workspace_root": str(tmp_path)})

    def test_rejects_invalid_workspace_root(self, tmp_path):
        """测试 workspace_root 必须是已存在的目录。"""
        tool = ReadFileTool()
        missing_root = tmp_path / "missing"
        file_root = tmp_path / "file.txt"
        file_root.write_text("not a directory", encoding="utf-8")

        with pytest.raises(ValueError, match="workspace_root"):
            tool.run({"path": "test.txt", "workspace_root": str(missing_root)})

        with pytest.raises(ValueError, match="workspace_root"):
            tool.run({"path": "test.txt", "workspace_root": str(file_root)})

    def test_rejects_path_outside_workspace(self, tmp_path):
        """测试拒绝工作区外的路径"""
        tool = ReadFileTool()
        outside_file = tmp_path.parent / "outside.txt"
        outside_file.write_text("secret", encoding="utf-8")

        with pytest.raises(ValueError, match="outside workspace"):
            tool.run({"path": "../outside.txt", "workspace_root": str(tmp_path)})

    def test_absolute_path_within_workspace(self, tmp_path):
        """测试工作区内的绝对路径"""
        tool = ReadFileTool()
        test_file = tmp_path / "test.txt"
        expected_content = "Absolute path test"
        test_file.write_text(expected_content, encoding="utf-8")

        result = tool.run({"path": str(test_file), "workspace_root": str(tmp_path)})
        assert result == expected_content

    def test_default_workspace_root(self, tmp_path, monkeypatch):
        """测试默认工作区根目录为当前目录"""
        tool = ReadFileTool()
        test_file = tmp_path / "test_default.txt"

        test_file.write_text("Default workspace test", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        result = tool.run({"path": "test_default.txt"})

        assert result == "Default workspace test"


class TestWriteFileTool:
    """测试 WriteFileTool 类"""

    def test_writes_content(self, tmp_path):
        """测试写入文件功能"""
        tool = WriteFileTool()
        test_file = tmp_path / "output.txt"
        content_to_write = "Test content for writing"

        result = tool.run({
            "path": "output.txt",
            "content": content_to_write,
            "workspace_root": str(tmp_path),
        })

        assert result == "ok"
        assert test_file.read_text(encoding="utf-8") == content_to_write

    def test_allows_empty_content(self, tmp_path):
        """测试空字符串是合法文件内容"""
        tool = WriteFileTool()
        test_file = tmp_path / "empty.txt"

        result = tool.run({
            "path": "empty.txt",
            "content": "",
            "workspace_root": str(tmp_path),
        })

        assert result == "ok"
        assert test_file.read_text(encoding="utf-8") == ""

    def test_rejects_missing_content(self, tmp_path):
        """测试缺少 content 参数"""
        tool = WriteFileTool()

        with pytest.raises(ValueError, match="content"):
            tool.run({"path": "test.txt", "workspace_root": str(tmp_path)})

        with pytest.raises(ValueError, match="content"):
            tool.run({"path": "test.txt", "content": None, "workspace_root": str(tmp_path)})

    def test_rejects_non_string_content(self, tmp_path):
        """测试写入内容必须是字符串，避免把 dict/list 静默转成伪文件内容。"""
        tool = WriteFileTool()

        with pytest.raises(TypeError, match="content"):
            tool.run({
                "path": "test.txt",
                "content": {"not": "text"},
                "workspace_root": str(tmp_path),
            })

        assert not (tmp_path / "test.txt").exists()

    def test_rejects_non_string_path(self, tmp_path):
        """测试写入路径必须是字符串，避免把数字等坏参数静默转成文件名。"""
        tool = WriteFileTool()

        with pytest.raises(TypeError, match="path"):
            tool.run({
                "path": 123,
                "content": "should not be written",
                "workspace_root": str(tmp_path),
            })

        assert not (tmp_path / "123").exists()

    def test_rejects_path_outside_workspace(self, tmp_path):
        """测试拒绝工作区外的路径"""
        tool = WriteFileTool()
        outside_file = tmp_path.parent / "outside.txt"
        outside_file.write_text("secret", encoding="utf-8")

        with pytest.raises(ValueError, match="outside workspace"):
            tool.run({
                "path": str(outside_file),
                "content": "new content",
                "workspace_root": str(tmp_path),
            })

        assert outside_file.read_text(encoding="utf-8") == "secret"

    def test_overwrites_existing_file(self, tmp_path):
        """测试覆盖现有文件"""
        tool = WriteFileTool()
        test_file = tmp_path / "existing.txt"
        test_file.write_text("Old content", encoding="utf-8")

        result = tool.run({
            "path": "existing.txt",
            "content": "New content",
            "workspace_root": str(tmp_path),
        })

        assert result == "ok"
        assert test_file.read_text(encoding="utf-8") == "New content"

    def test_creates_nested_directories(self, tmp_path):
        """测试自动创建嵌套目录"""
        tool = WriteFileTool()
        nested_file = tmp_path / "nested" / "dir" / "file.txt"
        content = "Nested directory test"

        result = tool.run({
            "path": "nested/dir/file.txt",
            "content": content,
            "workspace_root": str(tmp_path),
        })

        assert result == "ok"
        assert nested_file.read_text(encoding="utf-8") == content


class TestBackwardCompatibility:
    """测试向后兼容的函数形式"""

    def test_read_file_function(self, tmp_path):
        """测试 read_file 函数"""
        test_file = tmp_path / "test.txt"
        expected_content = "Function test"
        test_file.write_text(expected_content, encoding="utf-8")

        result = read_file({"path": "test.txt", "workspace_root": str(tmp_path)})
        assert result == expected_content

    def test_write_file_function(self, tmp_path):
        """测试 write_file 函数"""
        test_file = tmp_path / "output.txt"
        content_to_write = "Function write test"

        result = write_file({
            "path": "output.txt",
            "content": content_to_write,
            "workspace_root": str(tmp_path),
        })

        assert result == "ok"
        assert test_file.read_text(encoding="utf-8") == content_to_write


class TestToolRegistryIntegration:
    """测试工具注册表集成"""

    def test_can_register_with_tool_registry(self, tmp_path):
        """测试文件工具可以注册到 ToolRegistry 并通过 registry.run() 执行"""
        registry = ToolRegistry()

        # 注册工具实例
        read_tool = ReadFileTool()
        write_tool = WriteFileTool()
        registry.register(read_tool)
        registry.register(write_tool)

        # 测试读取文件
        test_file = tmp_path / "registry_test.txt"
        expected_content = "Tool registry test content"
        test_file.write_text(expected_content, encoding="utf-8")

        read_result = registry.run(
            "read_file",
            {"path": "registry_test.txt", "workspace_root": str(tmp_path)},
        )

        # 测试写入文件
        write_result = registry.run(
            "write_file",
            {
                "path": "registry_output.txt",
                "content": "Written via registry",
                "workspace_root": str(tmp_path),
            },
        )

        assert read_result == expected_content
        assert write_result == "ok"
        assert (tmp_path / "registry_output.txt").read_text(encoding="utf-8") == "Written via registry"

    def test_tool_names_and_descriptions(self):
        """测试工具的名称和描述"""
        read_tool = ReadFileTool()
        write_tool = WriteFileTool()

        assert read_tool.name == "read_file"
        assert write_tool.name == "write_file"
        assert "读取工作区内的文件内容" in read_tool.description
        assert "写入工作区内的文件内容" in write_tool.description

    def test_tool_registry_listing(self):
        """测试工具在注册表中的列表"""
        registry = ToolRegistry()
        read_tool = ReadFileTool()
        write_tool = WriteFileTool()

        registry.register(read_tool)
        registry.register(write_tool)

        tools = registry.list_tools()
        assert "read_file" in tools
        assert "write_file" in tools
        assert len(tools) == 2


class TestPathResolution:
    """测试路径解析功能"""

    def test_relative_path_resolution(self, tmp_path):
        """测试相对路径解析"""
        tool = ReadFileTool()
        nested_dir = tmp_path / "nested"
        nested_dir.mkdir()
        test_file = nested_dir / "test.txt"
        test_file.write_text("Nested test", encoding="utf-8")

        # 从子目录访问
        result = tool.run({
            "path": "test.txt",
            "workspace_root": str(nested_dir),
        })
        assert result == "Nested test"

    def test_dot_dot_path_within_workspace(self, tmp_path):
        """测试 .. 路径但在工作区内"""
        tool = ReadFileTool()
        nested_dir = tmp_path / "a" / "b"
        nested_dir.mkdir(parents=True)
        test_file = tmp_path / "a" / "test.txt"
        test_file.write_text("Parent test", encoding="utf-8")

        # 路径中包含 ..，但解析后仍然位于 workspace_root 内。
        result = tool.run({
            "path": "a/b/../test.txt",
            "workspace_root": str(tmp_path),
        })
        assert result == "Parent test"

    def test_symlink_resolution(self, tmp_path):
        """测试符号链接解析"""
        tool = ReadFileTool()

        # 创建真实文件
        real_file = tmp_path / "real.txt"
        real_file.write_text("Real content", encoding="utf-8")

        # 创建符号链接
        link_file = tmp_path / "link.txt"
        try:
            link_file.symlink_to(real_file)
        except OSError as exc:
            pytest.skip(f"当前环境不允许创建符号链接: {exc}")

        # 通过符号链接读取
        result = tool.run({
            "path": "link.txt",
            "workspace_root": str(tmp_path),
        })
        assert result == "Real content"

    def test_path_with_spaces(self, tmp_path):
        """测试包含空格的路径"""
        tool = WriteFileTool()

        result = tool.run({
            "path": "file with spaces.txt",
            "content": "Content with spaces",
            "workspace_root": str(tmp_path),
        })

        assert result == "ok"
        test_file = tmp_path / "file with spaces.txt"
        assert test_file.read_text(encoding="utf-8") == "Content with spaces"


class TestEditFileTool:
    """测试 EditFileTool 局部编辑工具"""

    def test_replaces_one_exact_text_block(self, tmp_path):
        """测试只替换一个明确文本片段。"""
        tool = file_tools.EditFileTool()
        test_file = tmp_path / "module.py"
        test_file.write_text(
            "def greet():\n"
            "    return 'hello'\n",
            encoding="utf-8",
        )

        result = tool.run({
            "path": "module.py",
            "old_text": "return 'hello'",
            "new_text": "return 'hi'",
            "workspace_root": str(tmp_path),
        })

        assert result == "ok"
        assert test_file.read_text(encoding="utf-8") == (
            "def greet():\n"
            "    return 'hi'\n"
        )

    def test_rejects_missing_old_text(self, tmp_path):
        """测试目标文本不存在时拒绝写入，避免静默无效编辑。"""
        tool = file_tools.EditFileTool()
        test_file = tmp_path / "module.py"
        original = "def greet():\n    return 'hello'\n"
        test_file.write_text(original, encoding="utf-8")

        with pytest.raises(ValueError, match="old_text was not found"):
            tool.run({
                "path": "module.py",
                "old_text": "return 'missing'",
                "new_text": "return 'hi'",
                "workspace_root": str(tmp_path),
            })

        assert test_file.read_text(encoding="utf-8") == original

    def test_rejects_old_text_that_appears_multiple_times(self, tmp_path):
        """测试目标文本出现多次时拒绝写入，避免误改多个语义位置。"""
        tool = file_tools.EditFileTool()
        test_file = tmp_path / "module.py"
        original = (
            "def first():\n"
            "    return 'same'\n"
            "\n"
            "def second():\n"
            "    return 'same'\n"
        )
        test_file.write_text(original, encoding="utf-8")

        with pytest.raises(ValueError, match="old_text appears multiple times"):
            tool.run({
                "path": "module.py",
                "old_text": "return 'same'",
                "new_text": "return 'changed'",
                "workspace_root": str(tmp_path),
            })

        assert test_file.read_text(encoding="utf-8") == original

    def test_rejects_empty_old_text(self, tmp_path):
        """测试空 old_text 会被拒绝，避免在所有字符间隙插入内容。"""
        tool = file_tools.EditFileTool()
        test_file = tmp_path / "module.py"
        original = "print('hello')\n"
        test_file.write_text(original, encoding="utf-8")

        with pytest.raises(ValueError, match="old_text"):
            tool.run({
                "path": "module.py",
                "old_text": "",
                "new_text": "print('hi')",
                "workspace_root": str(tmp_path),
            })

        assert test_file.read_text(encoding="utf-8") == original

    def test_rejects_non_string_new_text(self, tmp_path):
        """测试 new_text 必须是字符串，避免把坏参数写进文件。"""
        tool = file_tools.EditFileTool()
        test_file = tmp_path / "module.py"
        original = "print('hello')\n"
        test_file.write_text(original, encoding="utf-8")

        with pytest.raises(TypeError, match="new_text"):
            tool.run({
                "path": "module.py",
                "old_text": "hello",
                "new_text": {"not": "text"},
                "workspace_root": str(tmp_path),
            })

        assert test_file.read_text(encoding="utf-8") == original

    def test_rejects_path_outside_workspace(self, tmp_path):
        """测试继承文件工具 workspace_root 边界，不允许编辑工作区外文件。"""
        tool = file_tools.EditFileTool()
        outside_file = tmp_path.parent / "outside_edit.txt"
        outside_file.write_text("secret", encoding="utf-8")

        with pytest.raises(ValueError, match="outside workspace"):
            tool.run({
                "path": str(outside_file),
                "old_text": "secret",
                "new_text": "changed",
                "workspace_root": str(tmp_path),
            })

        assert outside_file.read_text(encoding="utf-8") == "secret"

    def test_edit_file_function_keeps_backward_compatible_function_style(self, tmp_path):
        """测试 edit_file 也提供函数形式，便于早期示例和测试直接调用。"""
        test_file = tmp_path / "notes.txt"
        test_file.write_text("old value\n", encoding="utf-8")

        result = file_tools.edit_file({
            "path": "notes.txt",
            "old_text": "old value",
            "new_text": "new value",
            "workspace_root": str(tmp_path),
        })

        assert result == "ok"
        assert test_file.read_text(encoding="utf-8") == "new value\n"

    def test_default_coding_registry_can_run_edit_file(self, tmp_path):
        """测试 edit_file 已进入默认 coding 工具注册表。"""
        registry = create_coding_tool_registry()
        test_file = tmp_path / "module.py"
        test_file.write_text("x = 1\n", encoding="utf-8")

        result = registry.run(
            "edit_file",
            {
                "path": "module.py",
                "old_text": "x = 1",
                "new_text": "x = 2",
                "workspace_root": str(tmp_path),
            },
        )

        assert result == "ok"
        assert test_file.read_text(encoding="utf-8") == "x = 2\n"


# 运行所有测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
