import os
import re
import csv
from pathlib import Path
from ingest.chunk import chunk_text
from ingest.embed import ingest_and_store


def ingest_transcripts(data_dir: str = "data/transcripts"):
    """Process YouTube transcripts from .txt files OR a CSV with a Transcript column."""
    transcript_dir = Path(data_dir)
    if not transcript_dir.exists():
        print(f"Directory not found: {data_dir}")
        return 0

    total_chunks = 0

    # Handle CSV files (YouTube channel backup format with Transcript column)
    csv_files = list(transcript_dir.glob("*.csv"))
    for filepath in csv_files:
        print(f"\nProcessing CSV: {filepath.name}")
        try:
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                row_count = 0
                for row in reader:
                    transcript = row.get("Transcript", "").strip()
                    title = row.get("Title", "").strip()
                    if not transcript or len(transcript) < 50:
                        continue

                    row_count += 1
                    # Clean transcript artifacts
                    transcript = re.sub(r'[\[\(]\d{1,2}:\d{2}(?::\d{2})?[\]\)]', '', transcript)
                    transcript = re.sub(r'^Speaker\s+\d+\s*:', '', transcript, flags=re.MULTILINE)

                    chunks = chunk_text(transcript, max_tokens=500, overlap_tokens=50)
                    source_name = title if title else filepath.name
                    count = ingest_and_store(
                        chunks=chunks,
                        source_type="youtube_transcript",
                        source_file=source_name,
                    )
                    total_chunks += count
                    if row_count % 10 == 0:
                        print(f"  Processed {row_count} videos...")

                print(f"  Processed {row_count} videos total from CSV.")
        except Exception as e:
            print(f"  Error parsing {filepath.name}: {e}")

    # Handle .txt files (individual transcript files)
    txt_files = list(transcript_dir.glob("*.txt"))
    for filepath in txt_files:
        print(f"\nProcessing: {filepath.name}")
        text = filepath.read_text(encoding="utf-8", errors="ignore")

        text = re.sub(r'[\[\(]\d{1,2}:\d{2}(?::\d{2})?[\]\)]', '', text)
        text = re.sub(r'^Speaker\s+\d+\s*:', '', text, flags=re.MULTILINE)

        chunks = chunk_text(text, max_tokens=500, overlap_tokens=50)
        count = ingest_and_store(
            chunks=chunks,
            source_type="youtube_transcript",
            source_file=filepath.name,
        )
        total_chunks += count

    if total_chunks == 0:
        print(f"No transcript files (.txt or .csv) found in {data_dir}")

    print(f"\nTotal transcript chunks ingested: {total_chunks}")
    return total_chunks


if __name__ == "__main__":
    ingest_transcripts()
