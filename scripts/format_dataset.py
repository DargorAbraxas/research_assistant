from research_assistant.format_dataset import format_json_db

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATASET_DIR = PROJECT_ROOT / "dataset" / "dataset_raw"
OUT_DATASET_DIR = PROJECT_ROOT / "dataset" / "paper_dataset"

format_json_db(RAW_DATASET_DIR, OUT_DATASET_DIR)
