from typing import Annotated
from pathlib import Path
from langchain_core.tools import tool
import os
import voyageai
from tidb_vector.integrations import TiDBVectorClient
from tidb_vector.integrations.vector_client import QueryResult
from dotenv import load_dotenv

load_dotenv()

_voyager_client: voyageai.Client | None = None
_vector_client: TiDBVectorClient | None = None


def _get_voyager_client() -> voyageai.Client:
    global _voyager_client
    if _voyager_client is not None:
        return _voyager_client
    api_key = os.getenv("VOYAGE_API_KEY")
    if not api_key:
        raise RuntimeError("VOYAGE_API_KEY is not set")
    _voyager_client = voyageai.Client(api_key=api_key)
    return _voyager_client


def _get_vector_client() -> TiDBVectorClient:
    global _vector_client
    if _vector_client is not None:
        return _vector_client
    conn = os.getenv("TIDB_CONNECTION_STRING")
    if not conn:
        raise RuntimeError("TIDB_CONNECTION_STRING is not set")
    _vector_client = TiDBVectorClient(
        connection_string=conn,
        vector_dimension=1024,
        table_name="sample_ecommerce_app_code",
        drop_existing_table=False,
    )
    return _vector_client


@tool
def get_data_from_embeddings(
    query: Annotated[str, "query for vector db"],
    top_K: Annotated[int, "No of nodes needs to be retried"] = 5,
) -> list[QueryResult]:
    """Retrieves the AST semantic nodes (abstract syntax tree–based code representations enriched with semantic metadata)
    of the project’s codebase from the vector database. This allows the agent to access relevant code structure, symbols,
    and relationships for tasks like debugging, refactoring, or answering stack-trace–related queries"""
    voyager = _get_voyager_client()
    vector_client = _get_vector_client()
    query_embedding = voyager.embed(
        texts=[query], model="voyage-code-3", input_type="query"
    ).embeddings[0]
    relevant_files = vector_client.query(query_vector=query_embedding, k=top_K)
    return relevant_files


if __name__ == "__main__":
    print(get_data_from_embeddings.invoke({"query": "is redis used in the project"}))


@tool
def get_file_content_from_path(
    path: Annotated[str, "file_path from the meta data of queryResult"],
) -> str:
    """Retrieves the content of the file from the path. Use this to get the full file content from the ast node's metadata"""
    path = Path(path)
    if path.is_file():
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            return f"error reading file: {e}"
    else:
        return "file not found"
