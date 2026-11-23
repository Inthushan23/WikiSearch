from langchain_core.tools import tool

from .domain.search.wiki_search import rag_search


@tool
def wikipedia_search(query: str):
    """Recherche des informations sur Wikipedia pour répondre à une question."""
    if query:
        print("QUERY: ", query)
        contexts = rag_search(query)
        if contexts:
            return "\n\n".join(contexts)
    return "No context could be retrieved"


if __name__ == "__main__":
    wikipedia_search()
