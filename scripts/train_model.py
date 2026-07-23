from research_assistant.train_model import train

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "dataset" / "paper_dataset"
OUTPUT_DIR = PROJECT_ROOT / "trained_model_output"

train(DATASET_DIR, OUTPUT_DIR)
