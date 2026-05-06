import math
import wikipediaapi as wk
import threading


_wiki_local = threading.local()

def get_wiki():
    if not hasattr(_wiki_local, "wiki"):
        _wiki_local.wiki = wk.Wikipedia(user_agent="user123", language='fr')
    return _wiki_local.wiki

def search(title: str, p: float = 0.1): # p est le pourcentage de la page à renvoyer (en partant du haut) si cette dernière existe
    wiki = get_wiki()
    page_py = wiki.page(title)
    if page_py.exists():
        content = page_py.text
        return content[: int(len(content)*p)]
    else: 
        return None
    
def get_summary(title: str, p: float = 1.0, thresh: int = math.inf):
    wiki = get_wiki()
    page_py = wiki.page(title)
    if page_py.exists():
        content = page_py.summary
        if len(content) > thresh:
            return content[: int(len(content)*p)]
        else:
            return content
    else: 
        return None
