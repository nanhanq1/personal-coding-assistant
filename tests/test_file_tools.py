import pytest

from pca.tools.base import Tool
from pca.tools.file_tools import read_file, write_file
from pca.tools.registry import ToolRegistry


def test_read_file_returns_content(tmp_path):
    """测试读取文件返回正确内容"""
    test_file = tmp_path / "test.txt"
    expected_content = "Hello, World!"
    test_file.write_text(expected_content, encoding="utf-8")

    result = read_file({"path": "test.txt", "workspace_root": str(tmp_path)})

    assert result == expected_content


def test_read_file_raises_when_file_missing():
    """测试文件不存在时抛出 FileNotFoundError"""
    with pytest.raises(FileNotFoundError):
        read_file({"path": "missing.txt"})


def test_write_file_writes_content(tmp_path):
    """测试写入文件功能"""
    test_file = tmp_path / "output.txt"
    content_to_write = "Test content for writing"

    result = write_file(
        {
            "path": "output.txt",
            "content": content_to_write,
            "workspace_root": str(tmp_path),
        }
    )

    assert result == "ok"
    assert test_file.read_text(encoding="utf-8") == content_to_write


def test_write_file_allows_empty_content(tmp_path):
    """测试空字符串是合法文件内容"""
    test_file = tmp_path / "empty.txt"

    result = write_file(
        {
            "path": "empty.txt",
            "content": "",
            "workspace_root": str(tmp_path),
        }
    )

    assert result == "ok"
    assert test_file.read_text(encoding="utf-8") == ""


def test_file_tools_reject_blank_path(tmp_path):
    """测试空路径会在工具边界被拒绝"""
    for invalid_path in ("", " ", None):
        with pytest.raises(ValueError, match="path"):
            read_file({"path": invalid_path, "workspace_root": str(tmp_path)})


def test_file_tools_reject_path_outside_workspace(tmp_path):
    """测试拒绝工作区外的路径"""
    outside_file = tmp_path.parent / "outside.txt"
    outside_file.write_text("secret", encoding="utf-8")

    with pytest.raises(ValueError, match="outside workspace"):
        read_file({"path": "../outside.txt", "workspace_root": str(tmp_path)})

    with pytest.raises(ValueError, match="outside workspace"):
        write_file(
            {
                "path": str(outside_file),
                "content": "new content",
                "workspace_root": str(tmp_path),
            }
        )

    assert outside_file.read_text(encoding="utf-8") == "secret"


def test_write_file_rejects_missing_content(tmp_path):
    """测试缺少 content 参数会暴露工具调用错误"""
    with pytest.raises(KeyError):
        write_file({"path": "test.txt", "workspace_root": str(tmp_path)})

    with pytest.raises(ValueError, match="content"):
        write_file({"path": "test.txt", "content": None, "workspace_root": str(tmp_path)})


def test_file_tools_can_register_with_tool_registry(tmp_path):
    """测试文件工具可以注册到 ToolRegistry 并通过 registry.run() 执行"""
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="read_file",
            description="读取工作区内的文件内容",
            handler=read_file,
        )
    )
    registry.register(
        Tool(
            name="write_file",
            description="写入工作区内的文件内容",
            handler=write_file,
        )
    )

    test_file = tmp_path / "registry_test.txt"
    expected_content = "Tool registry test content"
    test_file.write_text(expected_content, encoding="utf-8")

    read_result = registry.run(
        "read_file",
        {"path": "registry_test.txt", "workspace_root": str(tmp_path)},
    )
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
