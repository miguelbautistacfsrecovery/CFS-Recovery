import re
from pathlib import Path
from ingest.chunk import chunk_text
from ingest.embed import ingest_and_store

# Sections to include (curated - general concepts only, no internal coaching techniques)
INCLUDE_SECTIONS = [
    "Explaining the Disorder",
    "The PolyVagal Scale",
    "Red (Bedridden)",
    "Red Zone Description",
    "Orange (Mainly Housebound)",
    "Orange Zone Description",
    "Yellow (Functional + Intense Symptoms)",
    "Yellow Zone Description",
    "Green (Fully Functional + Minimal Symptoms)",
    "Green Zone Description",
    "Understanding Symptoms",
    "Primary Symptoms",
    "Secondary Symptoms",
    "Chronic Fatigue",
    "Brain Fog",
    "Chronic Pain",
    "Definitions & Key Words",
]

# Sections to EXCLUDE (internal coaching IP)
EXCLUDE_SECTIONS = [
    "Coaching Templates",
    "Polarity Template",
    "Growth mindset vs Fixed Mindset",
    "Mentorship Lunch Schedule",
    "Change Control",
    "30 Day Roadmap Examples",
    "Questions Repository",
    "Coaches approach",
]


def should_include_section(section_title: str) -> bool:
    title_lower = section_title.lower()
    for exc in EXCLUDE_SECTIONS:
        if exc.lower() in title_lower:
            return False
    for inc in INCLUDE_SECTIONS:
        if inc.lower() in title_lower:
            return True
    # Include symptom sections by default
    if "symptom" in title_lower:
        return True
    return False


def extract_sections(text: str) -> list[tuple[str, str]]:
    """Extract named sections from the playbook text."""
    # Split by section headers (lines that look like "5.1 Red Zone Description:")
    pattern = r'(?:^|\n)(\d+\.?\d*\.?\s+[A-Z].*?)(?=\n\d+\.?\d*\.?\s+[A-Z]|\Z)'
    sections = []

    lines = text.split('\n')
    current_title = ""
    current_content = []

    for line in lines:
        # Check if this is a section header
        if re.match(r'^\d+\.?\d*\.?\s+[A-Z]', line.strip()):
            if current_title and current_content:
                sections.append((current_title, '\n'.join(current_content)))
            current_title = line.strip().rstrip(':')
            current_content = []
        else:
            current_content.append(line)

    if current_title and current_content:
        sections.append((current_title, '\n'.join(current_content)))

    return sections


def ingest_playbook(playbook_path: str = "data/playbook/Recovery Playbook - JUNIOR DEVELOPMENT.txt"):
    """Process curated sections of the Recovery Playbook."""
    filepath = Path(playbook_path)
    if not filepath.exists():
        print(f"Playbook not found: {playbook_path}")
        return 0

    print(f"Processing playbook: {filepath.name}")
    text = filepath.read_text(encoding="utf-8", errors="ignore")

    # Remove Google Drive links and YouTube URLs (internal tools)
    text = re.sub(r'https?://(?:drive\.google\.com|www\.youtube\.com|youtu\.be)\S+', '', text)
    # Remove Loom links
    text = re.sub(r'https?://(?:www\.)?loom\.com\S+', '', text)
    # Remove LucidChart links
    text = re.sub(r'https?://lucid\.app\S+', '', text)

    sections = extract_sections(text)
    print(f"  Found {len(sections)} sections.")

    total_chunks = 0
    for title, content in sections:
        if not should_include_section(title):
            continue

        content = content.strip()
        if len(content) < 50:
            continue

        print(f"  Including: {title}")
        chunks = chunk_text(content, max_tokens=500, overlap_tokens=50)

        # Determine topic from section title
        topic = "general"
        title_lower = title.lower()
        if "red" in title_lower:
            topic = "red_zone"
        elif "orange" in title_lower:
            topic = "orange_zone"
        elif "yellow" in title_lower:
            topic = "yellow_zone"
        elif "green" in title_lower:
            topic = "green_zone"
        elif "symptom" in title_lower:
            topic = "symptoms"

        count = ingest_and_store(
            chunks=chunks,
            source_type="playbook",
            source_file=filepath.name,
            category="recovery_framework",
            topic=topic,
        )
        total_chunks += count

    print(f"\nTotal playbook chunks ingested: {total_chunks}")
    return total_chunks


if __name__ == "__main__":
    ingest_playbook()
