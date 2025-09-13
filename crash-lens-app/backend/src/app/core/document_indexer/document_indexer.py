import os
import urllib.request
from io import BytesIO

import fitz
import voyageai
from PIL import Image
from pymupdf import Pixmap
from tidb_vector.integrations import TiDBVectorClient
from dotenv import load_dotenv

from src.app.services.s3_service import S3Service

load_dotenv()


class DocumentIndexer:
    def __init__(self, document_url: str, repo_id: str):
        self.repo_id = repo_id
        self.url = document_url
        self.voyager = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
        self.vector_client = TiDBVectorClient(
            connection_string=os.getenv("TIDB_CONNECTION_STRING"),
            vector_dimension=1024,
            table_name=f"document_indexer_{repo_id}",
            drop_existing_table=True,
        )
        self.s3_service = S3Service()

    def index(self):
        with urllib.request.urlopen(self.url) as response:
            pdf_data = response.read()
        pdf_stream = BytesIO(pdf_data)
        pdf = fitz.open(stream=pdf_stream, filetype="pdf")
        images = []
        mat = fitz.Matrix(1.0, 1.0)
        for n in range(pdf.page_count):
            pix: Pixmap = pdf[n].get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        pdf.close()

        embeddings = self.voyager.multimodal_embed(
            inputs=[[image] for image in images],
            model="voyage-multimodal-3",
            input_type="document"
        ).embeddings
        urls = self.s3_service.upload_document_image(images)
        self.vector_client.insert(embeddings=embeddings, texts=urls)
        print("Documents indexed successfully")
