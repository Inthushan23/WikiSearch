from langchain_core.messages import HumanMessage
import requests
import time 
import sys

from config import URL, RESPONCE_LATENCY
from agents.utils.checking import sanity_check
from agents.utils.cli_responses import help


def format_question(user_quest):
    return {"messages": [HumanMessage(content= user_quest)]}


def delete_last_line():
    "Use this function to delete the last line in the STDOUT"
    sys.stdout.write('\x1b')
    sys.stdout.write('\x1b[2K')
    sys.stdout.write('\x1b[1A')

    sys.stdout.write("\n<AI> ")

def write_thinking():
    print("<AI> ", end = "", flush= True)
    message = "Thinking..."
    for c in message:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(0.05)


def conversation():
    if not sanity_check():
        print("exit")
        return 

    user_req = ""
    print("START CONV: ")
    while True:
        think_var: bool = False
        user_req = input("#<User> ") # user request
        if user_req.lower() == "/bye":
            break
        elif user_req.lower() == "/help":
            print(help())
            continue
        elif user_req == "":
            continue
        else:
            think_var = True
            write_thinking()
        try:
            with requests.post(url=f"{URL}/ask", params={"user_req": user_req}, stream=True) as response:
                
                for chunk in response.iter_content(chunk_size= None, decode_unicode=True):
                    if chunk:
                        if think_var:
                            delete_last_line()
                            think_var = False
                            
                        print(chunk, end = "", flush= True)
                        time.sleep(RESPONCE_LATENCY)

        except Exception as e:
            print(f"There is an issue - {e}")
            return 
        print()

if __name__ == "__main__":
    conversation()