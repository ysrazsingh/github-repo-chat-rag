from fastapi import FastAPI
from app.layers._0.schema import RepoInput
from app.layers._0.ingestion import run_ingest

app = FastAPI()

@app.get("/")
def index():
    return {"project": "github-repo-chat-rag"}


@app.post("/gitingest")
async def ingest(input: RepoInput):
    summary, tree, content = await run_ingest(input)
    full_context = f"{summary}\n\n{tree}\n\n{content}"
    
    return {
        "repo": input.repo_url,
        "summary": summary,
        "tree": tree,
        "content": content,
        "meta": {
            "tokens_estimate": len(full_context) // 4
        }
    }