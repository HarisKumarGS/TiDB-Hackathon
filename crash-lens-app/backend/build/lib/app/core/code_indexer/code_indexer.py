import os
from ..parser import ASTSemanticNode
from ..parser import AstCodeParser
import voyageai
from tidb_vector.integrations import TiDBVectorClient


class CodeIndexer:
    def __init__(self):
        self.voyager = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
        self.vector_client = TiDBVectorClient(
            connection_string=os.getenv("TIDB_CONNECTION_STRING"),
            vector_dimension=1024,
            table_name="sample_ecommerce_app_code",
            drop_existing_table=False,
        )

    def index(self, dir: str):
        parser = AstCodeParser()
        for root, dir, files in os.walk(dir):
            for file in files:
                file_path = os.path.join(root, file)
                nodes = parser.parse_file_to_ast(file_path)
                self.__save_embeddings(nodes)

    def __save_embeddings(self, nodes: list[ASTSemanticNode]):
        node_to_text = [
            text for node in nodes if (text := self.__ast_semantic_node_to_text(node))
        ]
        metadatas = [
            {
                "file_path": node.file_path,
                "type": node.type,
                "name": node.name,
                "line_start": node.line_start,
                "line_end": node.line_end,
                "language": node.language,
            }
            for node in nodes
        ]
        if node_to_text:
            embeddings = self.__text_to_embeddings(node_to_text, "document")
            self.vector_client.insert(
                texts=node_to_text, embeddings=embeddings, metadatas=metadatas
            )

    def __text_to_embeddings(self, texts: list[str], type: str) -> list[list[float]]:
        return self.voyager.embed(
            texts=texts, model="voyage-code-3", input_type=type
        ).embeddings

    def __ast_semantic_node_to_text(self, node: ASTSemanticNode) -> str:
        text = f"Type: {node.type}\nName: {node.name}\nContent: {node.content}\n"
        text += f"File: {node.file_path} ({node.line_start}-{node.line_end})\n"
        text += f"Language: {node.language}\n"
        if node.parameters:
            text += f"Parameters: {', '.join(node.parameters)}\n"
        if node.return_type:
            text += f"Return type: {node.return_type}\n"
        if node.imports:
            text += f"Imports: {', '.join(node.imports)}\n"
        if node.calls_to:
            text += f"Calls: {', '.join(node.calls_to)}\n"
        if node.parent_class:
            text += f"Parent class: {node.parent_class}\n"
        return text

    def findReleventFiles(self):
        stack_trace = (
            """What is the function that retrives all the products from the database?"""
        )
        query_embedding = self.__text_to_embeddings([stack_trace], "query")[0]
        relevant_files = self.vector_client.query(query_vector=query_embedding, k=2)
        print(relevant_files)
        print(f"Query vector")
        print(f"Relevant files: {relevant_files[0]}")
