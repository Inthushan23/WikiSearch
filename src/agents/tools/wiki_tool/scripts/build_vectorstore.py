from concurrent.futures import ThreadPoolExecutor, as_completed
from qdrant_client import models
# import tqdm

from ....utils.transform_utils.process_data import normalize
from ....utils.transform_utils.encoder import Encoder
from ....utils.loader_utils.load_data import load_filtered_text_data
from ..wiki_utils import add_context

from ..config import (
    WIKI_FILE_PATH,
    VEC_SIZE,
    ENCODER_MODEL,
    COLLECTION_NAME,
    MAX_WORKERS,
)
from ..client import qdrant_cli


def _init_vecstore():
    if not qdrant_cli:
        return False

    if not qdrant_cli.collection_exists(collection_name=COLLECTION_NAME):
        qdrant_cli.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VEC_SIZE, distance=models.Distance.COSINE
            ),
        )

    return True


def create_embeddings():
    # Init process
    points = []
    vec_init_state = _init_vecstore()

    if not vec_init_state:
        print("There is an issue with Qdrant...exit.")
        return

    ecd = Encoder(ENCODER_MODEL)  # encoder from Hugging face

    titles_lst = load_filtered_text_data(WIKI_FILE_PATH)
    if not titles_lst:
        print("Error when filtering text data")
        return

    data_ctx_titles = []  # contexts + titles
    print("DEBUG")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        print("DEBUG 1")
        futures = {
            executor.submit(add_context, title, 0.75, 400): (id, title)
            for id, title in enumerate(titles_lst)
        }
        print("DEBUG 2")
        for future in as_completed(futures):
            data = futures[future]  # id + title
            res = future.result()
            print(data)

            data_ctx_titles.append((data, res))

    print("END OF 'ADD CONTEXT'")
    id_title_data, ctx_titles = zip(*data_ctx_titles)

    norm_ctx_title = list(map(normalize, ctx_titles))
    embeddings = ecd.encode(norm_ctx_title, show_progress_bar=True)

    for elt, vec in zip(id_title_data, embeddings):
        id, title = elt
        print(id)
        point = models.PointStruct(id=id, vector=vec, payload={"title": title})
        points.append(point)

    # for id, title in tqdm.tqdm(enumerate(titles_lst)):
    #     ctx_title = add_context(title = title, p = 0.75, thresh = 400)
    #     norm_ctx_title = normalize(ctx_title)

    #     vec = ecd.encode(norm_ctx_title)

    #     point = models.PointStruct(id = id, vector = vec, payload={"title": title})
    #     points.append(point)

    qdrant_cli.upsert(collection_name=COLLECTION_NAME, points=points)


if __name__ == "__main__":
    create_embeddings()
