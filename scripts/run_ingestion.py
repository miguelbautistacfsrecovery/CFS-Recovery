#!/usr/bin/env python3
"""One-command data ingestion script. Run from the project root:

    python scripts/run_ingestion.py

Before running, copy your data files into the data/ directory:
    data/transcripts/   - YouTube transcript .txt files
    data/discord/        - Discord export .csv files
    data/playbook/       - Recovery Playbook .txt file
    data/calls/          - Call extraction .csv files
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from ingest.ingest_transcripts import ingest_transcripts
from ingest.ingest_discord import ingest_discord
from ingest.ingest_playbook import ingest_playbook
from ingest.ingest_calls import ingest_call_extractions


def main():
    print("=" * 60)
    print("THRIVER AI - Data Ingestion")
    print("=" * 60)

    total = 0

    print("\n--- YouTube Transcripts ---")
    total += ingest_transcripts("data/transcripts")

    print("\n--- Discord Coaching Logs ---")
    total += ingest_discord("data/discord")

    print("\n--- Recovery Playbook ---")
    total += ingest_playbook("data/playbook/Recovery Playbook - JUNIOR DEVELOPMENT.txt")

    print("\n--- Call Extractions ---")
    total += ingest_call_extractions("data/calls")

    print("\n" + "=" * 60)
    print(f"INGESTION COMPLETE: {total} total chunks stored.")
    print("=" * 60)


if __name__ == "__main__":
    main()
