from langchain_core.messages import HumanMessage
import requests

from src.config import URL
from src.agents.utils.checking import sanity_check
from src.agents.utils.cli_responses import help


def format_question(user_quest):
    return {"messages": [HumanMessage(content= user_quest)]}

def conversation():
    if not sanity_check():
        print("exit")
        return 

    user_req = ""
    print("START CONV: ")
    while True:
        user_req = input("#<User> ") # user request
        if user_req.lower() == "/bye":
            break
        elif user_req.lower() == "/help":
            print(help())
            continue
        elif user_req == "":
            continue
        
        try:
            res = requests.post(url=f"{URL}/ask", params={"user_req": user_req}).json() # response
        except Exception as e:
            print(f"There is an issue - {e}")
            return 
        print(f"#<AI> {res.get("response")}")