# mcp_schema.py

from typing import List
from dataclasses import dataclass

@dataclass
class Message:
    role: str
    content: str

class MCPContext:
    def __init__(self, context: List[Message] = None):
        self.context = context or []
    
    def add(self, role: str, content: str):
        self.context.append(Message(role=role, content=content))
