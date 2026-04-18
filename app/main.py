from fastapi import FastAPI
from app.layers._0.schema import RepoInput
from app.layers._0.ingestion import run_ingest
from app.layers._1.processing import process_gitingest_output
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

    return {
        "repo": input.repo_url,
        "total_chunks": len(chunks),
        "chunks": chunks[:100],
        "meta": {
            "deduplicated": True
        }
    }