import math
from .domain.search.wiki_fetch import get_summary


def add_context(title: str, p: float = 1.0, thresh: int = math.inf):
    context = get_summary(title, p, thresh)
    if context:
        up_title = title + "\t" + context
        return up_title
    else:
        return None