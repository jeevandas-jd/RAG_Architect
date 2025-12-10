


def text_chunker(text, chunk_size,overlap):
    text = text.replace("\r", " ").replace("\n", " ")
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        # move with overlap
        start = end - overlap
        if start < 0:
            start = 0
    return chunks
