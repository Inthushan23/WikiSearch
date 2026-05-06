from fastapi import FastAPI
from src.agents.graph_agent import comp_graph
from src.agents.io import format_question


agent_app = FastAPI()

@agent_app.get("/health")
def check_sanity():
    return {"status": "200"}

@agent_app.post("/ask")
def invoke(user_req: str):
    config = {"configurable": {"thread_id": "user-123"}}
    f_quest = format_question(user_req)
    res = comp_graph.invoke(f_quest, config=config)

    return {"response": res["messages"][-1].content}
    