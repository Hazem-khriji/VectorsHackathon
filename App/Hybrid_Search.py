from qdrant_client import QdrantClient, models


class HybridSearcher:
    DENSE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    SPARSE_MODEL = "Qdrant/bm25"
    LATE_INTERACTION_MODEL = "colbert-ir/colbertv2.0"

    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.qdrant_client = QdrantClient(url="http://localhost:6333")


    def search(self, text: str,filters=None):
        search_result = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            prefetch=[
                models.Prefetch(
                    query=models.Document(text=text, model=self.DENSE_MODEL),
                    using="text-dense",
                    limit=5
                ),
                models.Prefetch(
                    query=models.Document(text=text, model=self.SPARSE_MODEL),
                    using="text-sparse",
                    limit=5
                ),
            ],
            query=models.Document(text=text, model=self.LATE_INTERACTION_MODEL),
            using="text-late-interaction",
            with_payload=True,
            query_filter=filters,
            limit=5,
        ).points
        metadata = [point.payload for point in search_result]
        return metadata

