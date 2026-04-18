from app.layers._2.embedding import embed_batch

def choose_top_k(query: str):
    q_len = len(query.split())

    if q_len < 5:
        return 4
    elif q_len < 15:
        return 8
    else:
        return 12


def embed_query(query: str):
    return embed_batch([query])[0]

def similarity_search(collection, query, top_k=8):
    query_embedding = embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    hits = []

    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        hits.append({
            "text": doc,
            "file_path": meta["file_path"],
            "start_line": meta["start_line"],
            "end_line": meta["end_line"],
            "distance": dist
        })

    return hits

def filter_hits(hits, max_distance=0.4):
    return [h for h in hits if h["distance"] <= max_distance]


def rerank_simple(query, hits):
    query_terms = set(query.lower().split())

    def score(hit):
        text = hit["text"].lower()
        overlap = sum(1 for t in query_terms if t in text)
        return (hit["distance"], -overlap)

    return sorted(hits, key=score)


def rerank_with_llm(query, hits):
    prompt = f"""
Rank the following code snippets by relevance to the query:

Query: {query}

Snippets:
{[h['text'][:300] for h in hits]}
"""

    return hits


def merge_adjacent(hits):
    hits = sorted(hits, key=lambda x: (x["file_path"], x["start_line"]))

    merged = []
    prev = None

    for h in hits:
        if prev and h["file_path"] == prev["file_path"] and h["start_line"] <= prev["end_line"] + 5:
            prev["text"] += "\n" + h["text"]
            prev["end_line"] = h["end_line"]
        else:
            if prev:
                merged.append(prev)
            prev = h

    if prev:
        merged.append(prev)

    return merged


def assemble_context(hits, max_chars=12000):
    hits = sorted(hits, key=lambda x: x["distance"])

    context = ""
    used = set()

    for h in hits:
        key = (h["file_path"], h["start_line"])

        if key in used:
            continue

        block = (
            f"\n\nFILE: {h['file_path']} "
            f"({h['start_line']}-{h['end_line']})\n"
            f"{h['text']}"
        )

        if len(context) + len(block) > max_chars:
            break

        context += block
        used.add(key)

    return context

def retrieve_context(collection, query):
    top_k = choose_top_k(query)

    hits = similarity_search(collection, query, top_k)

    hits = filter_hits(hits)

    hits = rerank_simple(query, hits)

    hits = merge_adjacent(hits)

    context = assemble_context(hits)

    return {
        "query": query,
        "top_k": top_k,
        "num_hits": len(hits),
        "context": context,
        "hits": hits[:5]
    }