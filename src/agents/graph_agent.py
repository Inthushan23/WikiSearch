import json
import re

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from src.agents.agent_state import AgentState
from src.config import AGENT_URL, MODEL
from .tools import wikipedia_search


load_llm = ChatOllama(model= MODEL, base_url= AGENT_URL)

tools = [wikipedia_search]
llm = load_llm.bind_tools(tools=tools)

mask = re.compile(r'\{.*"outputs".*\}', re.DOTALL)


def response(state: AgentState):
    messages = [SystemMessage(content="Tu es un assistant. Utilise wiki_tool pour les questions factuelles."), *state["messages"]]
    res = llm.invoke(messages) 
    print("TEST: ", messages)
    return {"context": "", "messages": [res]}


            
def route_tools(state: AgentState):
    last_msg = state["messages"][-1]
    if getattr(last_msg, "tool_calls", None):
        return "tools"
    return END

tool_node = ToolNode(tools)


graph = StateGraph(AgentState)

graph.add_node("response", response)
graph.add_node("tools", tool_node)

graph.add_edge(START, "response")
graph.add_conditional_edges("response", route_tools, {"tools": "tools", END: END})
graph.add_edge("tools", "response")

checkpoiter = MemorySaver()
comp_graph = graph.compile(checkpointer=checkpoiter)