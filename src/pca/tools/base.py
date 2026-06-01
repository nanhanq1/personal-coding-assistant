"""Tool base abstractions will be implemented in Week 1 Day 2."""
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Tool:
    name : str
    description : str
    handler : Callable[[dict[str,Any]],Any]

    def run(self,arguments:dict[str,Any]) -> Any:
        return self.handler(arguments)

