
import chromadb
import hashlib

client = chromadb.Client(
    chromadb.config.Settings(
        persist_directory="./chroma_db"
    )
)


def get_collection(repo_url: str):
    repo_name = repo_url.replace("https://github.com/", "").replace("/", "_")

    return client.get_or_create_collection(
        name=repo_name,
        metadata={"source": "github"}
    )



def generate_id(chunk):
    base = f"{chunk['file_path']}|{chunk['start_line']}|{chunk['chunk']}"
    return hashlib.md5(base.encode()).hexdigest()


def store_chunks(collection, chunks):
    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for c in chunks:
        cid = generate_id(c)

        ids.append(cid)
        documents.append(c["chunk"])
        embeddings.append(c["embedding"])
        metadatas.append({
            "file_path": c["file_path"],
            "start_line": c["start_line"],
            "end_line": c["end_line"]
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )