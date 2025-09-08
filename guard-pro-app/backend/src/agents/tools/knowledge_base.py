import os
import voyageai
from tidb_vector.integrations import TiDBVectorClient


class KnowledgeBase:
    def __init__(self):
        self.voyager = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
        self.vector_client = TiDBVectorClient(
            connection_string=os.getenv("TIDB_CONNECTION_STRING"),
            vector_dimension=1024,
            table_name="sample_ecommerce_app_code",
            drop_existing_table=False,
        )

    def query(self, query: str, top_k: int = 5) -> str:
        query_embedding = self.__text_to_embeddings([query], "query")[0]
        relevant_files = self.vector_client.query(query_vector=query_embedding, k=top_k)
        print(relevant_files)
        return f"relevant_files: {relevant_files}"
