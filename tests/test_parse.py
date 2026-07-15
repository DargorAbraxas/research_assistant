from research_assistant.parse import MarkdownCleaner
import pytest

@pytest.mark.parametrize(
    "text,expected",
    [
        ("Introduction\n12\nMethods", "Introduction\nMethods"),
        ("1\n Here is something", " Here is something"),
        ("This is Figure 2 in the paper.", "This is Figure 2 in the paper."),
        ("Without numbers ", "Without numbers ")
    ],
)
def test_remove_page_numbers(text, expected):
    '''
    The function removes lines with numbers only. Empty lines and spaces after deletion are handled in other function
    '''
    cleaner = MarkdownCleaner()
    assert cleaner.clean(text) == expected

@pytest.mark.parametrize(
    "text,expected",
    [
        ("<!--Start of picture text-->. Some text to delete <!--End of picture text-->", ""),
        ("<!-- Start of picture text -->. Some text to delete here\nwith\nmultilines <!-- End of picture text -->", ""),
        ("<!--START OF PICTURE TEXT --> FORMAT \nWITH CAPS <!-- End of picture text -->\nNormal text", "Normal text"),
        # ("There is some <!--START OF PICTURE TEXT --> FORMAT \nWITH CAPS <!-- End of picture text -->text parsed here", "There is some text parsed here"),
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
    ],
)
def test_remove_picture_blocks(text, expected):
    cleaner = MarkdownCleaner()
    assert cleaner.clean(text) == expected

@pytest.mark.parametrize(
    "text,expected",
    [
        ("Intro\n\nMethods\nSome methods", "Intro\n\nMethods\nSome methods"),
        ("Intro\n\n\t\nMethods\nSome methods", "Intro\n\nMethods\nSome methods"),
        ("Line1\nLine2", "Line1\nLine2"),
        ("Line1\n \nLine2", "Line1\n\nLine2")
    ],
)
def test_remove_empty_lines(text, expected):
    cleaner = MarkdownCleaner()
    assert cleaner.clean(text) == expected
