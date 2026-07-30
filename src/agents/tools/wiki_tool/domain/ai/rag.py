from ...config import COLLECTION_NAME, ENCODER_MODEL, RAG_THRESHOLD, RAG_RETRIEVE_LIMIT
from ...client import qdrant_cli
from .build_vectorstore import create_update_embeddings
from .....utils.transform_utils.encoder import Encoder
from .....utils.transform_utils.process_data import normalize


model = Encoder(ENCODER_MODEL) # Il faut le charger qu'une fois

def rag_query(query: str):
    if not qdrant_cli.collection_exists(collection_name= COLLECTION_NAME):
        state = create_update_embeddings(COLLECTION_NAME)
        if not state:
            return False

    norm_query = normalize(query)
    vec_query = model.encode(norm_query)

    res = qdrant_cli.query_points(collection_name=COLLECTION_NAME, query=vec_query, limit= RAG_RETRIEVE_LIMIT)   
    hits = res.points

    matches = [hit.payload['title'] for hit in hits if hit.score > RAG_THRESHOLD]
    
    return matches


if __name__ == "__main__":
    query = "Qui est le joueur de League of Lengend, T1 Faker ?"
    print(rag_query(query=query))