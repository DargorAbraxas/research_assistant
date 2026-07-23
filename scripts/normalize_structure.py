from research_assistant.normalize_sections import normalize_sections

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STRUCTURE_DIR = PROJECT_ROOT / "json"

normalize_sections(STRUCTURE_DIR)
