from pydantic import BaseModel, Field


class ConfigGraph(BaseModel):
    model_name: str
    url: str
    username: str


class UserRequest(BaseModel):
    user_req: str
    username: str
    model_name: str
    thread_id: str
