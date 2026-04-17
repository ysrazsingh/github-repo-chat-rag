from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from gitingest import ingest, ingest_async
from http import HTTPStatus

app = FastAPI()

@app.get("/")
def index():
    return {"project": "github-repo-chat-rag"}

# ---------- INPUT MODEL --------
class RepoInput(BaseModel):
    repo_url: str
    max_file_size: Optional[int] = 100_000
    include_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    use_async: bool = True

# ---------- CORE FUNCTION --------
async def run_ingest(input:RepoInput):
    try:
        if input.use_async:
            summary, tree, content = await ingest_async(
                input.repo_url,
                max_file_size=input.max_file_size,
                include_patterns=input.include_patterns,
                exclude_patterns=input.exclude_patterns,
            )
        else:
            summary, tree, content = ingest(
                input.repo_url,
                max_file_size=input.max_file_size,
                include_patterns=input.include_patterns,
                exclude_patterns=input.exclude_patterns,
            )
        return summary, tree, content
    except Exception as e:
        raise HTTPException(
            status_code = HTTPStatus.INTERNAL_SERVER_ERROR,
            detail = str(e)
        )

# ---------- ENDPOINT --------

@app.post("/gitingest")
async def ingest(input: RepoInput):
    summary, tree, content = await run_ingest(input)
    
    full_context = f"{summary}\n\n{tree}\n\n{content}"

    return {
        "repo": input.repo_url,
        "summary": summary,
        "tree": tree,
        "content": content,
        "full_context": full_context,
        "meta": {
            "tokens_estimate": len(full_context) // 4  # rough estimate
        }
    }