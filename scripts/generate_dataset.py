from research_assistant.generate_dataset import generate

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

STRUCTURE_DIR = PROJECT_ROOT / "json"
DATASET_DIR = PROJECT_ROOT / "dataset" / "dataset_raw"

generate(STRUCTURE_DIR, DATASET_DIR)
