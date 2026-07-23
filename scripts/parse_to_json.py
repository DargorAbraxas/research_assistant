from research_assistant.structure_json import parse_md_json

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
JSON_DIR = PROJECT_ROOT / "json"

parse_md_json(DATA_DIR, JSON_DIR)
