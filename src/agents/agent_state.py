from typing import Annotated, NotRequired, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    context: NotRequired[str]
    tools: NotRequired[list[str]]
    use_tools: NotRequired[bool]