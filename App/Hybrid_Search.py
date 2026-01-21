from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer


class HybridSearcher:
    DENSE_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    SPARSE_MODEL = "prithivida/Splade_PP_en_v1"

    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.qdrant_client = QdrantClient(url="http://localhost:6333")


    def search(self, text: str):
        search_result = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=models.FusionQuery(
                fusion=models.Fusion.RRF
            ),
            prefetch=[
                models.Prefetch(
                    query=self.DENSE_MODEL.encode(text).tolist(),
                    using="text-dense",
                ),
                models.Prefetch(
                    query=models.Document(text=text, model=self.SPARSE_MODEL),
                    using="text-sparse",
                ),
            ],
            query_filter=None,
            limit=5,
        ).points
        metadata = [point.payload for point in search_result]
        return metadata

