"""运行时与工作区相关模块包。"""

from pca.runtime.interface import CommandRuntime
from pca.runtime.docker_runtime import DockerRuntime


# 修改前旧代码：
# __all__ = ["CommandRuntime"]
#
# 问题：Day 5 新增 DockerRuntime 后，包入口仍只暴露 CommandRuntime，
# 后续集成需要绕到具体模块导入 adapter。
__all__ = ["CommandRuntime", "DockerRuntime"]
