from fastapi import FastAPI
from fastapi.responses import StreamingResponse

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
    async def generator():
        async for (chunk, metadata) in comp_graph.astream(f_quest, stream_mode= "messages", config=config):
            if metadata["langgraph_node"] in ["response", "agent"]:
                if chunk.content:
                    yield chunk.content

    return StreamingResponse(generator(), media_type= "text/plain")
    