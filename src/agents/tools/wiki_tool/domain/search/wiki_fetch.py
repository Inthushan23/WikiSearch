import math
import threading
import wikipediaapi as wk


_wiki_local = threading.local()

def get_wiki():
    if not hasattr(_wiki_local, "wiki"):
        _wiki_local.wiki = wk.Wikipedia(user_agent="user123", language='fr')
    return _wiki_local.wiki

# On récupère le bloc d'introduction d'une page (un résumé du sujet)
def get_summary(title: str, p: float = 1.0, thresh: int = math.inf): # thresh: on applique la réduction p, si le résumé contient plus de caractères que thresh
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