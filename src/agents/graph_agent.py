from langgraph.graph import StateGraph, END, START
from langchain_core.messages import AIMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver

from src.agents.agent_state import AgentState
from src.config import AGENT_URL, MODEL

llm = ChatOllama(model= MODEL, base_url= AGENT_URL)


def response(state: AgentState):
    res = llm.invoke(state["messages"])
    return {"messages": [AIMessage(res.content)]}

graph = StateGraph(AgentState)

graph.add_node("response", response)
graph.add_edge(START, "response")
graph.add_edge("response", END)

checkpoiter = MemorySaver()
comp_graph = graph.compile(checkpointer=checkpoiter)