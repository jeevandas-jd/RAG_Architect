
from extractText import extract_text_from_pdf
from TextChunk import chunk_text

if __name__ == "__main__":
    file_path = "sample.pdf"  # Replace with your file path
    text = extract_text_from_pdf(file_path)
    
    chunk_size = 100  # Number of words per chunk
    overlap = 20      # Number of overlapping words between chunks
    
    chunks = chunk_text(text, chunk_size, overlap)
    
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}:\n{chunk}\n")