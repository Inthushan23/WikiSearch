from pydantic import BaseModel


class ConfigGraph(BaseModel):
    model_name: str


class UserRequest(BaseModel):
    user_req: str
    model_name: str
    thread_id: str
