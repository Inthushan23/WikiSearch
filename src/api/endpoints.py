from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from agents.io import format_question
from api.schemas import UserRequest, ConfigGraph
from agents.graph_manager import GraphManager
from agents.memory_manager import MemoryManager

agent_app = FastAPI()

graph_manager = GraphManager()
memory_manager = MemoryManager()


@agent_app.get("/health")
def check_sanity():
    return {"status": "200"}


@agent_app.post("/config-graph")
def config_graph(config: ConfigGraph):
    graph_name = config.username + "-" + config.model_name

    checkpointer = memory_manager.create_memory(graph_name=graph_name)

    graph_manager.build_load_graph(
        username=config.username,
        model_name=config.model_name,
        url=config.url,
        memory=checkpointer,
    )
    return {"graph_name": graph_name, "status": "200"}


@agent_app.post("/ask")
async def invoke(request: UserRequest):
    config = {"configurable": {"thread_id": request.thread_id}}

    f_quest = format_question(request.user_req)  # formatted query
    graph_name = request.username + "-" + request.model_name

    async def generator():
        async for chunk, metadata in graph_manager.get_graph(graph_name).astream(
            f_quest, stream_mode="messages", config=config
        ):
            if metadata["langgraph_node"] in ["response", "agent"]:
                if chunk.content:
                    yield chunk.content

    return StreamingResponse(generator(), media_type="text/plain")
