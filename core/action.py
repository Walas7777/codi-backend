from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Action:
    type: str
    tool: str
    params: Dict[str, Any]
