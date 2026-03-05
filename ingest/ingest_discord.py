import csv
import re
from pathlib import Path
from ingest.chunk import chunk_text
from ingest.embed import ingest_and_store

# Coach usernames to filter for
COACH_USERNAMES = {
    "miguelbautista",
    "cristataylor",
    "crista",
    "nicoleclark",
    "jonlevene",
    "adrianne4353",
    "adrianne",
}


def strip_client_names(text: str, known_names: set[str] = None) -> str:
    """Remove client names from text for privacy."""
    # Remove @mentions
    text = re.sub(r'@\w+', '[member]', text)
    # Remove "Hey [Name]," patterns at start
    text = re.sub(r'^(?:Hey|Hi|Hello)\s+\w+,?\s*', '', text, flags=re.IGNORECASE)
    return text


def parse_discord_csv(filepath: Path) -> list[dict]:
    """Parse a Discord export CSV and return coach messages."""
    messages = []
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                username = row.get("Username", "").strip().lower()
                content = row.get("Content", "").strip()
                if not content:
                    continue
                # Check if this is a coach message
                is_coach = any(coach in username for coach in COACH_USERNAMES)
                if is_coach:
                    messages.append({
                        "username": username,
                        "content": content,
                        "date": row.get("Date", ""),
                    })
    except Exception as e:
        print(f"  Error parsing {filepath.name}: {e}")
    return messages


def group_consecutive_messages(messages: list[dict]) -> list[str]:
    """Group consecutive messages from the same coach into single texts."""
    if not messages:
        return []

    grouped = []
    current_group = [messages[0]["content"]]
    current_user = messages[0]["username"]

    for msg in messages[1:]:
        if msg["username"] == current_user:
            current_group.append(msg["content"])
        else:
            text = "\n\n".join(current_group)
            text = strip_client_names(text)
            if len(text) > 50:  # Skip very short messages
                grouped.append(text)
            current_group = [msg["content"]]
            current_user = msg["username"]

    # Don't forget the last group
    text = "\n\n".join(current_group)
    text = strip_client_names(text)
    if len(text) > 50:
        grouped.append(text)

    return grouped


def ingest_discord(data_dir: str = "data/discord"):
    """Process Discord CSV exports."""
    discord_dir = Path(data_dir)
    if not discord_dir.exists():
        print(f"Directory not found: {data_dir}")
        return 0

    csv_files = list(discord_dir.glob("*.csv"))
    if not csv_files:
        print(f"No .csv files found in {data_dir}")
        return 0

    total_chunks = 0
    for filepath in csv_files:
        print(f"\nProcessing: {filepath.name}")
        messages = parse_discord_csv(filepath)
        if not messages:
            print(f"  No coach messages found.")
            continue

        grouped_texts = group_consecutive_messages(messages)
        print(f"  Found {len(grouped_texts)} coach message groups.")

        all_chunks = []
        for text in grouped_texts:
            chunks = chunk_text(text, max_tokens=500, overlap_tokens=50)
            all_chunks.extend(chunks)

        if all_chunks:
            count = ingest_and_store(
                chunks=all_chunks,
                source_type="discord_coaching",
                source_file=filepath.name,
            )
            total_chunks += count

    print(f"\nTotal Discord chunks ingested: {total_chunks}")
    return total_chunks


if __name__ == "__main__":
    ingest_discord()
