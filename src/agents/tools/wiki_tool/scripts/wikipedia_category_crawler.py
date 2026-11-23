from __future__ import annotations

import csv
import time
from collections import deque
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests


API_URL = "https://fr.wikipedia.org/w/api.php"

ROOT_CATEGORY = "Catégorie:Paris"
OUTPUT_FILE = "articles_paris.csv"

MAX_DEPTH = 2

HEADERS = {
    "User-Agent": "WikipediaCategoryCrawler/1.0 (personal research; Python requests)"
}


def get_category_members(
    session: requests.Session,
    category_title: str,
) -> list[dict]:
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category_title,
        "cmtype": "page|subcat",
        "cmlimit": "max",
        "format": "json",
        "maxlag": 5,
    }

    members = []

    while True:
        for attempt in range(8):
            try:
                response = session.get(
                    API_URL,
                    params=params,
                    headers=HEADERS,
                    timeout=60,
                )

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")

                    if retry_after:
                        try:
                            delay = float(retry_after)
                        except ValueError:
                            retry_date = parsedate_to_datetime(retry_after)
                            delay = max(
                                0,
                                (
                                    retry_date - datetime.now(timezone.utc)
                                ).total_seconds(),
                            )
                    else:
                        delay = min(5 * (2**attempt), 300)

                    print(
                        f"[429] Wikipédia limite les requêtes. "
                        f"Nouvelle tentative dans {delay:.0f}s..."
                    )
                    time.sleep(delay)
                    continue

                if response.status_code in (500, 502, 503, 504):
                    delay = min(5 * (2**attempt), 300)
                    print(f"[{response.status_code}] Nouvelle tentative dans {delay}s")
                    time.sleep(delay)
                    continue

                response.raise_for_status()
                payload = response.json()

                if payload.get("error", {}).get("code") == "maxlag":
                    print("[maxlag] Attente de 10 secondes...")
                    time.sleep(10)
                    continue

                if "error" in payload:
                    raise RuntimeError(
                        f"Erreur API pour {category_title}: {payload['error']}"
                    )

                members.extend(payload["query"]["categorymembers"])

                continuation = payload.get("continue")

                if not continuation:
                    return members

                params.update(continuation)
                break

            except requests.RequestException:
                if attempt == 7:
                    raise

                delay = min(5 * (2**attempt), 300)
                print(f"Erreur réseau. Nouvelle tentative dans {delay}s...")
                time.sleep(delay)

        else:
            raise RuntimeError(
                f"Impossible de récupérer les membres de "
                f"{category_title} après plusieurs tentatives."
            )


def crawl_category_tree(root_category: str, max_depth: int = 5) -> list[str]:
    """
    Explore récursivement les sous-catégories
    jusqu'à une profondeur maximale.
    """

    with requests.Session() as session:
        categories_to_visit = deque([(root_category, 0)])

        visited_categories: set[str] = set()
        article_titles: set[str] = set()

        while categories_to_visit:
            category, depth = categories_to_visit.popleft()

            if category in visited_categories:
                continue

            visited_categories.add(category)

            print(f"[Profondeur {depth}/{max_depth}] {category}")

            members = get_category_members(session, category)

            for member in members:
                namespace = member["ns"]
                title = member["title"]

                if namespace == 0:
                    article_titles.add(title)

                elif namespace == 14 and depth < max_depth:
                    if title not in visited_categories:
                        categories_to_visit.append((title, depth + 1))

            time.sleep(0.1)

    return sorted(article_titles, key=str.casefold)


def main() -> None:
    titles = crawl_category_tree(ROOT_CATEGORY, max_depth=MAX_DEPTH)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["title"])
        writer.writerows([[title] for title in titles])

    print("\nExtraction terminée.")
    print(f"Catégorie racine : {ROOT_CATEGORY}")
    print(f"Profondeur maximale : {MAX_DEPTH}")
    print("Catégories explorées : extraction terminée")
    print(f"Nombre d'articles uniques : {len(titles)}")
    print(f"Fichier créé : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
