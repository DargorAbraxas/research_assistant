from research_assistant.parse import MarkdownCleaner
import pytest
from pathlib import Path

@pytest.mark.parametrize(
    "text,expected",
    [
        ("<!--Start of picture text-->. Some text to delete <!--End of picture text-->", ""),
        ("<!-- Start of picture text -->. Some text to delete here\nwith\nmultilines <!-- End of picture text -->", ""),
        ("<!--START OF PICTURE TEXT --> FORMAT \nWITH CAPS <!-- End of picture text -->\nNormal text", "Normal text"),
        ("Here is some happy path", "Here is some happy path")
    ],
)
def test_remove_picture_blocks(text, expected):
    cleaner = MarkdownCleaner()
    assert cleaner.clean(text) == expected

@pytest.mark.parametrize(
    "text,expected",
    [
        ("\n**Figure 1**: Here\n\n", ""),
        ("*Figure 1*: Caption\n\nSome more text", "Some more text"),
    ],
)
def test_remove_picture_blocks(text, expected):
    cleaner = MarkdownCleaner()
    assert cleaner.clean(text) == expected


# =========================================================
# Here is a collection of real snippets of papers
# in order to test the proper functionality as a whole
# =========================================================
@pytest.mark.parametrize(
    "corpus_filename, expected_filename",
    [
        ("case_1.md", "case_1.md"),
        ("case_2.md", "case_2.md"),
        ("case_3.md", "case_3.md"),
        ("figure_in_text.md", "figure_in_text.md"),
        ("remove_figure.md", "remove_figure.md"),
        ("keep_figure_paragraph.md", "keep_figure_paragraph.md"),
        ("remove_page_number.md", "remove_page_number.md"),
        ("remove_corresponding_author.md", "remove_corresponding_author.md"),
        ("remove_affiliation.md", "remove_affiliation.md")
    ],
)
def test_snippets(corpus_filename, expected_filename):
    text = Path(f"tests/parse_corpus/{corpus_filename}").read_text()
    expected = Path(f"tests/parse_expected/{expected_filename}").read_text()

    cleaner = MarkdownCleaner()
    assert cleaner.clean(text) == expected
