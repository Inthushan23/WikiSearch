from .domain.search.wiki_search import rag_search


def ask_rag(query: str):
    if query:
        print("QUERY: ", query)
        contexts = rag_search(query)
        if contexts:
            return "\n\n".join(contexts)
    return ""


if __name__ == "__main__":
    ask_rag()