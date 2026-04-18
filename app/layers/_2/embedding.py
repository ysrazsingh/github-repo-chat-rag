from tenacity import retry, wait_exponential, stop_after_attempt
from openai import OpenAI
import os

EMBED_MODEL = "text-embedding-3-small"
MAX_TOKENS_PER_CHUNK = 8000

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def estimate_tokens(text):
    return len(text) // 4

def filter_chunks(chunks):
    return [
        c for c in chunks
        if estimate_tokens(c["chunk"]) < MAX_TOKENS_PER_CHUNK
    ]


def batch_chunks(chunks, batch_size=50):
    for i in range(0, len(chunks), batch_size):
        yield chunks[i:i + batch_size]


@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(5))
def embed_batch(texts):
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts
    )
    return [item.embedding for item in response.data]

def embed_chunks(chunks):
    # filter chunks
    chunks = filter_chunks(chunks)

    # batch chunks
    all_embeddings = []
    for batch in batch_chunks(chunks, batch_size=50):
        texts = [c["chunk"] for c in batch]
        # embed batch
        embeddings = embed_batch(texts)

        for chunk, emb in zip(batch, embeddings):
            chunk["embedding"] = emb
            all_embeddings.append(chunk)

    return all_embeddings