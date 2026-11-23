import chainlit as cl
from chainlit.input_widget import TextInput
import httpx
import yaml

from config import URL


with open("auth.yaml", "r") as file:
    users_config = yaml.safe_load(file)

users = users_config["users"]
for user in users:
    print(user)


@cl.password_auth_callback
async def auth_callback(username: str, password: str):
    for user in users:
        if user["username"] == username and user["password"] == password:
            return cl.User(identifier=username)

    return None


@cl.on_chat_start
async def start():
    await cl.ChatSettings(
        [
            TextInput(id="MODEL", label="Model's Name"),
            TextInput(id="MODEL_URL", label="Model's URL"),
        ]
    ).send()


@cl.on_settings_update
async def update_settings(settings):
    payload = {
        "model_name": settings.get("MODEL"),
        "url": settings.get("MODEL_URL"),
        "username": cl.user_session.get("user").identifier,
    }

    if not payload["model_name"] or not payload["url"]:
        return
    cl.user_session.set("MODEL", settings.get("MODEL"))
    cl.user_session.set("MODEL_URL", settings.get("MODEL_URL"))

    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url=URL + "/config-graph", json=payload)

        response.raise_for_status()


@cl.on_message
async def on_message(message: cl.Message):
    # Récupération de l'identifiant de conversation
    thread_id = cl.context.session.thread_id
    username = cl.user_session.get("user").identifier
    model_name = cl.user_session.get("MODEL")
    response = cl.Message(content="")
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            URL + "/ask",
            json={
                "user_req": message.content,
                "username": username,
                "model_name": model_name,
                "thread_id": thread_id,
            },
        ) as api_response:
            api_response.raise_for_status()

            async for chunk in api_response.aiter_text():
                if chunk:
                    await response.stream_token(chunk)

    await response.send()


@cl.on_chat_resume
async def on_chat_resume(thread):
    thread_id = thread["id"]
    print(f"Reprise de la conversation : {thread_id}")
