from research_assistant.download import download_arxiv

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

download_arxiv(DATA_DIR)
