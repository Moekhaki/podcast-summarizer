# mcp_schema.py

from typing import List, Literal
from pydantic import BaseModel

# Define allowed agent roles
Role = Literal[
    "user",
    "transcriber",
    "segmenter",
    "summarizer",
    "explainer",
    "chatbot"
]



# A single message/interaction in the protocol
class Message(BaseModel):
    role: Role
    content: str

# The full context = list of messages
class MCPContext(BaseModel):
    context: List[Message]

    def add(self, role: Role, content: str):
        self.context.append(Message(role=role, content=content))

    def as_dict(self) -> dict:
        return {"context": [msg.dict() for msg in self.context]}

    def display(self):
        for msg in self.context:
            print(f"[{msg.role.upper()}]\n{msg.content}\n")
