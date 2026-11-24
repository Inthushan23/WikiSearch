import ollama
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, trim_messages
from langchain_core.runnables import RunnableLambda
from langchain_ollama import ChatOllama
from langgraph.prebuilt import ToolNode

from agents.agent_state import AgentState
from agents.tools import wikipedia_search


def get_context_length(model_name: str, url: str) -> int:
    client = ollama.Client(host=url)

    response = client.show(model_name)

    for key, value in response.modelinfo.items():
        if key.endswith(".context_length"):
            return int(value)

    raise RuntimeError("Context length introuvable")


def build_graph(model: str, url: str, username: str):
    tools = [wikipedia_search]
    tool_node = ToolNode(tools)
    name = username + "-" + model

    llm = ChatOllama(name=name, model=model, base_url=url)

    llm = llm.bind_tools(tools=tools)

    context_length = get_context_length(model_name=model, url=url)
    max_context_length = int(context_length * 0.8)

    trimmer = RunnableLambda(
        lambda messages: trim_messages(
            messages,
            max_tokens=max_context_length,
            strategy="last",
            include_system=True,
            token_counter=llm,
        )
    )
    chain = trimmer | llm

    def response(state: AgentState):
        messages = [
            SystemMessage(
                content="Tu es un assistant qui doit répondre aux requetes de l'utilisateur. Tu dois  toujours founir une réponse."
            ),
            *state["messages"],
        ]
        res = chain.invoke(messages)
        return {"messages": [res]}

    def route_tools(state: AgentState):
        print("HISTORIQUE: ", state["messages"])
        last_msg = state["messages"][-1]
        if getattr(last_msg, "tool_calls", None):
            return "tools"
        return END

    def agent(state: AgentState):
        messages = [*state["messages"]]
        res = chain.invoke(messages)

        return {"messages": [res]}

    graph = StateGraph(AgentState)

    graph.add_node("response", response)
    graph.add_node("tools", tool_node)
    graph.add_node("agent", agent)

    graph.add_edge(START, "response")
    graph.add_conditional_edges("response", route_tools, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    graph.add_edge("agent", END)

    return graph
