import re
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(enc.encode(text))


def split_into_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text: str, max_tokens: int = 500, overlap_tokens: int = 50) -> list[str]:
    """Split text into chunks of approximately max_tokens with overlap."""
    # Clean the text
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = text.strip()

    if not text:
        return []

    # Split by paragraphs first, then by sentences
    paragraphs = text.split('\n\n')
    sentences = []
    for para in paragraphs:
        para_sentences = split_into_sentences(para)
        sentences.extend(para_sentences)
        sentences.append("")  # Paragraph break marker

    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        if sentence == "":
            # Paragraph break - add a newline to current chunk
            if current_chunk and current_chunk[-1] != "\n":
                current_chunk.append("\n")
            continue

        sentence_tokens = count_tokens(sentence)

        # If single sentence exceeds max, just add it as its own chunk
        if sentence_tokens > max_tokens:
            if current_chunk:
                chunks.append(" ".join(current_chunk).replace(" \n ", "\n\n").strip())
                current_chunk = []
                current_tokens = 0
            chunks.append(sentence)
            continue

        if current_tokens + sentence_tokens > max_tokens and current_chunk:
            chunk_text_str = " ".join(current_chunk).replace(" \n ", "\n\n").strip()
            chunks.append(chunk_text_str)

            # Keep overlap sentences
            overlap_chunk = []
            overlap_count = 0
            for s in reversed(current_chunk):
                if s == "\n":
                    continue
                s_tokens = count_tokens(s)
                if overlap_count + s_tokens > overlap_tokens:
                    break
                overlap_chunk.insert(0, s)
                overlap_count += s_tokens

            current_chunk = overlap_chunk
            current_tokens = overlap_count

        current_chunk.append(sentence)
        current_tokens += sentence_tokens

    if current_chunk:
        chunk_text_str = " ".join(current_chunk).replace(" \n ", "\n\n").strip()
        if chunk_text_str:
            chunks.append(chunk_text_str)

    return chunks
