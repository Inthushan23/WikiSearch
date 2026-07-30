from concurrent.futures import ThreadPoolExecutor, as_completed
from qdrant_client import models
# import tqdm

from .....utils.transform_utils.process_data import normalize
from .....utils.transform_utils.encoder import Encoder
from .....utils.loader_utils.load_data import load_filtered_text_data
from ...wiki_utils import add_context

from ...config import WIKI_FILE_PATH, VEC_SIZE, ENCODER_MODEL, COLLECTION_NAME, MAX_WORKERS
from ...client import qdrant_cli


def _init_vecstore(coll_name: str):
    if not qdrant_cli:
        return False
    
    if not qdrant_cli.collection_exists(collection_name= coll_name):
        qdrant_cli.create_collection(
            collection_name = coll_name,
            vectors_config = models.VectorParams(size= VEC_SIZE, distance= models.Distance.COSINE),
        )

    return True


def create_update_embeddings(coll_name : str = COLLECTION_NAME):
    # Init process
    points = []
    vec_init_state = _init_vecstore(coll_name=coll_name)

    if not vec_init_state:
        print("There is an issue with Qdrant...exit.")
        return
    
    ecd = Encoder(ENCODER_MODEL) # encoder from Hugging face

    titles_lst = load_filtered_text_data(WIKI_FILE_PATH)
    if not titles_lst:
        print("Error when filtering text data")
        return
    
    data_ctx_titles = [] # contexts + titles
    with ThreadPoolExecutor(max_workers = MAX_WORKERS) as executor:
    
        futures = {executor.submit(add_context, title, 0.75, 400): (id, title) for id, title in enumerate(titles_lst)}

        for future in as_completed(futures):
            data = futures[future] # id + title
            res = future.result()
            print(data)

            if res:
                data_ctx_titles.append((data, res))

    print("END OF 'ADD CONTEXT'")
    if not data_ctx_titles:
        print("No context found for wiki titles")
        return False

    id_title_data, ctx_titles = zip(*data_ctx_titles)
    
    norm_ctx_title = list(map(normalize, ctx_titles))
    embeddings = ecd.encode(norm_ctx_title, show_progress_bar= True)

    for elt, vec, ctx_title in zip(id_title_data, embeddings, ctx_titles):
        id, title = elt
        print(id)
        point = models.PointStruct(id = id, vector = vec, payload={"title": title, "context": ctx_title})
        points.append(point)

   
    try:
        qdrant_cli.upsert(
            collection_name=coll_name,
            points=points
        )
    except Exception as e:
        print(f"There is an error when upserting vectors into Qdrant - {e}")
        return False
    
    return True


if __name__ == "__main__":
    create_update_embeddings()