import json
import pytest
from research_assistant.structure_json import add_from_metadata, add_sections, structure_json
from pathlib import Path

@pytest.mark.parametrize(
    "paper_init_dir",
    [
        "case_1"
    ]
)
def test_add_from_metadata(paper_init_dir):
    paper_dir = Path(f"tests/json_corpus/{paper_init_dir}")

    expected_meta = Path(f"tests/json_expected/{paper_init_dir}_meta.json")
    json_expected = json.load(expected_meta.open())
    output_dict = add_from_metadata(paper_dir, {})

    assert output_dict == json_expected

@pytest.mark.parametrize(
    "paper_init_dir",
    [
        "case_1"
    ]
)
def test_add_sections(paper_init_dir):
    paper_dir = Path(f"tests/json_corpus/{paper_init_dir}")

    expected_body = Path(f"tests/json_expected/{paper_init_dir}_body.json")
    json_expected = json.load(expected_body.open())
    output_dict = add_sections(paper_dir, {})

    assert output_dict == json_expected

@pytest.mark.parametrize(
    "paper_init_dir",
    [
        "case_1"
    ]
)
def test_add_sections(paper_init_dir):
    paper_dir = Path(f"tests/json_corpus/{paper_init_dir}")

    expected_body = Path(f"tests/json_expected/{paper_init_dir}.json")
    json_expected = json.load(expected_body.open())
    output_dict = structure_json(paper_dir)

    assert output_dict == json_expected
    