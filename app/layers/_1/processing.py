import re
import hashlib


def split_into_files(content:str):
    pattern = r"=+\nFILE: (.*?)\n=+\n"
    matches = list(re.finditer(pattern, content))

    files = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        
        file_path = match.group(1).strip()
        file_content = content[start:end].strip()

        files.append({
            "path": file_path,
            "content": file_content
        })

    return files


def chunk_file(file_data, chunk_size=500, overlap=100):
    text = file_data["content"]
    lines = text.split("\n")

    chunks = []
    current_text = ""
    start_line = 1

    for i, line in enumerate(lines):
        current_text += line + "\n"

        if len(current_text) >= chunk_size:
            chunks.append({
                "chunk": current_text.strip(),
                "file_path": file_data["path"],
                "start_line": start_line,
                "end_line": i + 1
            })

            start_line = i + 1
            current_text = current_text[-overlap:]  # overlap

    if current_text.strip():
        chunks.append({
            "chunk": current_text.strip(),
            "file_path": file_data["path"],
            "start_line": start_line,
            "end_line": len(lines)
        })

    return chunks

def deduplicate_chunks(chunks):
    seen = set()
    unique_chunks = []
    
    for c in chunks:
        h = hashlib.md5(c["chunk"].encode()).hexdigest()

        if h not in seen:
            seen.add(h)
            c["chunk_id"] = h
            unique_chunks.append(c)

    return unique_chunks


def process_gitingest_output(content:str):
    # split into files
    files = split_into_files(content)

    # create chunks of files
    all_chunks = []
    for f in files:
        chunks = chunk_file(f)
        all_chunks.extend(chunks)

    # dedupliate chunks
    unique_chunks = deduplicate_chunks(all_chunks)

    return unique_chunks