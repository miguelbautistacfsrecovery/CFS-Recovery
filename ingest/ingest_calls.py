import csv
from pathlib import Path
from ingest.embed import ingest_and_store


def ingest_call_extractions(data_dir: str = "data/calls"):
    """Process call extraction CSVs. Each row is already a well-segmented chunk."""
    calls_dir = Path(data_dir)
    if not calls_dir.exists():
        print(f"Directory not found: {data_dir}")
        return 0

    csv_files = list(calls_dir.glob("*.csv"))
    if not csv_files:
        print(f"No .csv files found in {data_dir}")
        return 0

    total_chunks = 0
    for filepath in csv_files:
        print(f"\nProcessing: {filepath.name}")
        chunks = []
        categories = []
        topics = []
        coaches = []

        try:
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    content = row.get("Content", "").strip()
                    if not content or len(content) < 30:
                        continue

                    category = row.get("Category", "").strip()
                    topic = row.get("Context/Topic", row.get("Topic", "")).strip()
                    coach = row.get("Coach", "").strip()

                    chunks.append(content)
                    categories.append(category.lower().replace(" ", "_"))
                    topics.append(topic.lower())
                    coaches.append(coach)
        except Exception as e:
            print(f"  Error parsing {filepath.name}: {e}")
            continue

        if not chunks:
            print(f"  No valid rows found.")
            continue

        print(f"  Found {len(chunks)} coaching insights.")

        # Store each chunk individually with its category and topic
        for i, (chunk, cat, topic, coach) in enumerate(zip(chunks, categories, topics, coaches)):
            count = ingest_and_store(
                chunks=[chunk],
                source_type="call_extraction",
                source_file=filepath.name,
                category=cat,
                topic=topic,
                metadata={"coach": coach} if coach else {},
            )
            total_chunks += count

            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(chunks)} rows...")

    print(f"\nTotal call extraction chunks ingested: {total_chunks}")
    return total_chunks


if __name__ == "__main__":
    ingest_call_extractions()
