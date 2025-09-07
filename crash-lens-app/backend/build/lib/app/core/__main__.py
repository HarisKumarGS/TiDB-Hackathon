from .code_indexer import CodeIndexer
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    indexer = CodeIndexer()
    # indexer.index(
    #     "/Users/riyazurrazak/Development/hackathon/TiDB-Hackathon/sample-ecommerce-app"
    # )
    indexer.findReleventFiles()
