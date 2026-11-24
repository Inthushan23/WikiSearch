import math
import wikipediaapi as wk
import threading

from ..ai.rag import rag_query
from ...config import CONTENT_LENGTH_THRESH


_wiki_local = threading.local()


def get_wiki():
    if not hasattr(_wiki_local, "wiki"):
        _wiki_local.wiki = wk.Wikipedia(user_agent="user123", language="fr")
    return _wiki_local.wiki


def search(
    title: str, p: float = 0.1, thresh: int = math.inf
):  # p est le pourcentage de la page à renvoyer (en partant du haut de la page) si cette dernière existe
    wiki = get_wiki()
    page_py = wiki.page(title)
    if page_py.exists():
        content = page_py.text
        if len(content) > thresh:
            return content[: int(len(content) * p)]
        return content
    else:
        return None


def rag_search(query: str):
    titles = rag_query(query=query)

    if not titles:
        return False
    contexts: list[str] = []
    for title in titles:
        res = search(title=title, p=0.5, thresh=CONTENT_LENGTH_THRESH)
        if res:
            contexts.append(res)

    return contexts
