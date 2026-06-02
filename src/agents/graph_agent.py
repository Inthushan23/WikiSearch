import json
import re

from langgraph.graph import StateGraph, START
from langchain_core.messages import AIMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver

from src.agents.agent_state import AgentState
from src.config import AGENT_URL, MODEL
from .tools import ask_rag 


llm = ChatOllama(model= MODEL, base_url= AGENT_URL)
mask = re.compile(r'\{.*"outputs".*\}', re.DOTALL)


def _message_content(message):
    return getattr(message, "content", str(message))

def response(state: AgentState):
    context = state.get("context", "")
    print("CONTEXTE: ", context)
    prompt = f"""
# HISTORIQUE des échanges utilisateur/Assistant:
{state["messages"]}

# CONTEXTE pour répondre à la question précédente:
{context}

- Consigne: Tu dois répondre à la DERNIERE REPONSE de l'utilisateur en te basant sur l'HISTORIQUE et le CONTEXTE. Tu dois répondre de manière naturelle dans ton rôle d'assistant.

"""
    res = llm.invoke(prompt) # Convertir en liste ?
    return {"context": "", "messages": [AIMessage(res.content)]}

def decide_tools(state: AgentState):
    prompt = f"""
    Liste des tools que tu peux utiliser:
    - {{"Name": "wiki_tool", 
        "Description": "Ce tool permet de faire des recherches sur wikipedia, afin de récupérer des informations pour répondre à l'utilisateur.",
        "Usage": "Tu peux utiliser cet outil pour appuyer ton argumentation, t'aider à répondre aux questions. Tu ne dois pas t'en servir pour répondre à des affirmation sans contexte."}}

    L'utilisateur t'as répondu:
    {state["messages"][-1]}

    Règle:
    - Tu peux utiliser un tool parmi la liste disponible pour répondre à l'utilisateur. 
    - Lorsque tu veux utiliser un ou plusieurs tools, tu dois renvoyer leur nom uniquement. EXEMPLE: {{"outputs" : ["wiki_tool"]}}
    - Lorsque tu ne veux pas utiliser de tool, tu dois renvoyer {{"outputs" : []}}
    """
    try:
        res = llm.invoke(prompt).content 
        match = mask.search(res)
        if match:
            dict_res = json.loads(match.group(0))
            selected_tools = dict_res["outputs"]
        else: 
            selected_tools = None
        
    except Exception as e:
        print("Error: ", e)
        return 
    print("SELECTED TOOLS: ", selected_tools)
    if selected_tools:
        return {"tools": selected_tools, "use_tools": True}
    else:
        return {"tools": [], "use_tools": False}

            
def route_tools(state: AgentState):
    if state.get("use_tools", False) == True:
        return "use_tools"
    else:
        return "response"
# ajouter une fonction pour utiliser le tool
# Passer le contexte dans la discussion

def use_tools(state: AgentState):
    selected_tools = state.get("tools", [])
    
    if selected_tools:
        ret_context = ""
        for t_name in selected_tools:
            if t_name.lower() == "wiki_tool":
                query = _message_content(state["messages"][-1])
                res = ask_rag(query)
                if res:
                    ret_context += f"TOOL: {t_name}\nTOOL OUTPUT:\n{res}\n"

        
        return {"context": ret_context, "tools": [], "use_tools": False}
    else:
        return {"context": "CONTEXTE INDISPONIBLE", "tools": [], "use_tools": False}


graph = StateGraph(AgentState)

graph.add_node("response", response)
graph.add_node("use_tools", use_tools)
graph.add_node("decide_tools", decide_tools)

graph.add_edge(START, "decide_tools")
graph.add_edge("use_tools", "response")

graph.add_conditional_edges("decide_tools", route_tools, {"use_tools": "use_tools", "response": "response"})

checkpoiter = MemorySaver()
comp_graph = graph.compile(checkpointer=checkpoiter)