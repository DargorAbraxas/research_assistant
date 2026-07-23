from research_assistant.generate_dataset import get_section_data
from pathlib import Path
import json
import pytest

def test_get_section_data():
    paper_dict = json.loads(Path(f"tests/generate_corpus/paper_1.json").read_text())
    standardized_dict = json.loads(Path(f"tests/generate_corpus/standard_1.json").read_text())
    section = "introduction"

    assert get_section_data(paper_dict, standardized_dict, section) == paper_dict["sections"][0]["content"]

    # Multi paragraph
    section = "method"
    assert get_section_data(paper_dict, standardized_dict, section) == paper_dict["sections"][2]["content"] + "\n\n" + paper_dict["sections"][3]["content"]

    # No section found
    section = "discussion"
    assert get_section_data(paper_dict, standardized_dict, section) == None
