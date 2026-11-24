import chainlit as cl
from chainlit.input_widget import Select
import httpx

from config import URL


@cl.on_chat_start
async def start():
    cl.user_session.set("MODEL", "qwen3.5:4b")
    await cl.ChatSettings(
        [
            Select(
                id="MODEL",
                label="Ollama - Model",
                values=["qwen3.5:4b"],
                initial_index=0,
            )
        ]
    ).send()


@cl.on_settings_update
async def update_settings(settings):
    payload = {"model_name": settings.get("MODEL")}

    cl.user_session.set("MODEL", settings.get("MODEL"))

    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url=URL + "/config-graph", json=payload)

        response.raise_for_status()


@cl.on_message
async def on_message(message: cl.Message):
    # Récupération de l'identifiant de conversation
    thread_id = cl.context.session.thread_id
    model_name = cl.user_session.get("MODEL")

    response = cl.Message(content="")

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            URL + "/ask",
            json={
                "user_req": message.content,
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
