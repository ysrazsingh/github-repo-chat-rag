from pydantic import BaseModel
from typing import Optional, List

class RepoInput(BaseModel):
    repo_url: str
    max_file_size: Optional[int] = 100_000
    include_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    use_async: bool = True