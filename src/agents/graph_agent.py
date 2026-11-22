from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from agents.agent_state import AgentState
from config import AGENT_URL, MODEL
from .tools import wikipedia_search


def build_graph(model: str, url: str, username: str):
    tools = [wikipedia_search]
    tool_node = ToolNode(tools)
    name = username + "-" + model
   
    llm = ChatOllama(name= name, model= model, base_url= url)
    
    llm = llm.bind_tools(tools=tools)
    
    def response(state: AgentState):
        messages = [SystemMessage(content="Tu es un assistant qui doit répondre aux requetes de l'utilisateur. Tu dois  toujours founir une réponse. Utilise wiki_tool pour les questions factuelles."), *state["messages"]]
        res = llm.invoke(messages) 
        return {"messages": [res]}

                
    def route_tools(state: AgentState):
        print("HISTORIQUE: ", state["messages"])
        last_msg = state["messages"][-1]
        if getattr(last_msg, "tool_calls", None):
            return "tools"
        return END

    def agent(state: AgentState):
        messages = [*state["messages"]]
        res = llm.invoke(messages) 
        return {"messages": [res]}

    graph = StateGraph(AgentState)

    graph.add_node("response", response)
    graph.add_node("tools", tool_node)
    graph.add_node("agent", agent)

    graph.add_edge(START, "response")
    graph.add_conditional_edges("response", route_tools, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    graph.add_edge("agent", END)

    # checkpoiter = MemorySaver()
    # comp_graph = graph.compile(checkpointer=checkpoiter)
    return graph