from fastapi import FastAPI

# The file where HybridSearcher is stored
from App.Hybrid_Search import HybridSearcher

app = FastAPI()

# Create a neural searcher instance
hybrid_searcher = HybridSearcher(collection_name="products")


@app.get("/api/search")
def search_startup(q: str):
    return {"result": hybrid_searcher.search(text=q)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
