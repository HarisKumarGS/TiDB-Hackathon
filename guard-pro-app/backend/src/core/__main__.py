from .code_indexer import CodeIndexer

if __name__ == "__main__":
    indexer = CodeIndexer()
    # indexer.index(
    #     "/Users/riyazurrazak/Development/hackathon/TiDB-Hackathon/sample-ecommerce-app"
    # )
    indexer.findReleventFiles()
