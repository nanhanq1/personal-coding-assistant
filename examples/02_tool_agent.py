import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pca.tools import create_coding_tool_registry


def main() -> None:
    """展示默认 coding 工具注册表导出的工具 schema。"""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    registry = create_coding_tool_registry()
    schemas = registry.list_tool_schemas()
    print(json.dumps(schemas, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
