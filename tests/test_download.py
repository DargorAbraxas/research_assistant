from pathlib import Path
from unittest.mock import Mock, patch

from research_assistant.download import format_name
from research_assistant.download import download_arxiv

def test_format_name():
    assert format_name("2401.12345") == "2401.12345"
    assert format_name("cs/9912017") == "cs_9912017"
    assert format_name("CS/9912017") == "cs_9912017"

@patch("research_assistant.download.urlretrieve")
@patch("research_assistant.download.arxiv.Client")
def test_download_arxiv(mock_client_cls, mock_urlretrieve, tmp_path):
    # Creates a paper Mock
    paper = Mock()
    paper.get_short_id.return_value = "2401.12345"
    paper.pdf_url = "https://example.com/test.pdf"

    # Creates a mock client instance
    mock_client = Mock()
    mock_client.results.return_value = [paper]
    mock_client_cls.return_value = mock_client

    assert download_arxiv(tmp_path, max_results=1) == 1

    mock_urlretrieve.assert_called_once_with(
        "https://example.com/test.pdf",
        tmp_path / "2401.12345.pdf"
    )
