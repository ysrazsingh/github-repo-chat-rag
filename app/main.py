from fastapi import FastAPI
from app.layers._0.schema import RepoInput
from app.layers._0.ingestion import run_ingest
from app.layers._1.processing import process_gitingest_output
from app.layers._2.embedding import embed_chunks
from app.layers._3.storage import get_collection, store_chunks
from app.layers._4.retrieval import retrieve_context
from app.layers._5.generation import generate_answer


app = FastAPI()

@app.get("/")
def index():
    return {"project": "github-repo-chat-rag"}


@app.post("/gitingest")
async def ingest(input: RepoInput):
    # summary, tree, content = await run_ingest(input)
    # full_context = f"{summary}\n\n{tree}\n\n{content}"
    with open("output.txt", "r") as file:
        content = file.read()

    chunks = process_gitingest_output(content)
    chunks = embed_chunks(chunks)

    collection = get_collection(input.repo_url)
    store_chunks(collection, chunks)

    return {
        "repo": input.repo_url,
        "stored_chunks": len(chunks)
    }


@app.post("/ask")
async def ask(query: str, repo_url: str):
    collection = get_collection(repo_url)

    retrieval = retrieve_context(collection, query)

    context = retrieval["context"]

    answer = generate_answer(query, context)

    return {
        "query": query,
        "answer": answer,
        "sources": retrieval["hits"][:3]  # top sources
    }