import pandas as pd


def process_csv(path: str) -> None:
    df = pd.read_csv(path)
    lst = df["title"].tolist()
    formatted_list = list(map(lambda x: x.replace(" ", "_"), lst))
    print(formatted_list)

    with open("paris_articles.txt", "w+", encoding="utf-8") as f:
        for item in formatted_list:
            f.write("%s\n" % item)


if __name__ == "__main__":
    PATH = "articles_paris.csv"
    process_csv(PATH)
