from research_assistant.parse import parse_data

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

parse_data(DATA_DIR)
