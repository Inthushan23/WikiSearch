import requests 

from src.config import URL


def sanity_check():
    try:
        sanity = requests.get(url=f"{URL}/health").json()
        if sanity.get("status") == "200":
            return True
        else: 
            return False
        
    except  Exception as e:
        print(f"Error - {e}")
        return False