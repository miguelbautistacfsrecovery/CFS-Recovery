import os
from pathlib import Path
from ingest.chunk import chunk_text
from ingest.embed import ingest_and_store


def ingest_transcripts(data_dir: str = "data/transcripts"):
    """Process YouTube transcript .txt files."""
    transcript_dir = Path(data_dir)
    if not transcript_dir.exists():
        print(f"Directory not found: {data_dir}")
        return 0

    txt_files = list(transcript_dir.glob("*.txt"))
    if not txt_files:
        print(f"No .txt files found in {data_dir}")
        return 0

    total_chunks = 0
    for filepath in txt_files:
        print(f"\nProcessing: {filepath.name}")
        text = filepath.read_text(encoding="utf-8", errors="ignore")

        # Clean transcript artifacts (timestamps, filler)
        import re
        # Remove common timestamp formats like [00:00:00] or (00:00)
        text = re.sub(r'[\[\(]\d{1,2}:\d{2}(?::\d{2})?[\]\)]', '', text)
        # Remove speaker labels like "Speaker 1:" if present
        text = re.sub(r'^Speaker\s+\d+\s*:', '', text, flags=re.MULTILINE)

        chunks = chunk_text(text, max_tokens=500, overlap_tokens=50)
        count = ingest_and_store(
            chunks=chunks,
            source_type="youtube_transcript",
            source_file=filepath.name,
        )
        total_chunks += count

    print(f"\nTotal transcript chunks ingested: {total_chunks}")
    return total_chunks


if __name__ == "__main__":
    ingest_transcripts()
