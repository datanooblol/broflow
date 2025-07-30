from dataclasses import dataclass, field
from typing import Dict, Any, Literal, Protocol
from uuid import uuid4
from broflow.utils import get_timestamp

@dataclass
class Context:
    context: str
    id: str = field(default_factory=lambda: str(uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    type: Literal["document"] = "document"
    created_at: str = field(default_factory=get_timestamp)

class ModelInterface(Protocol):
    def run(self, system_prompt:str, messages:list)->str: return "string"
    def UserMessage(self, text:str, **kwargs)->str|None: pass
    def AIMessage(self, text:str, **kwargs)->str|None: pass