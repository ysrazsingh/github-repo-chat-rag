from fastapi import HTTPException
from http import HTTPStatus

from gitingest import ingest, ingest_async

from app.layers._0.schema import RepoInput


async def run_ingest(input: RepoInput):
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