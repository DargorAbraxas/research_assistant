import json
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import HTTPError
from datetime import datetime

from research_assistant.download import format_name, download_arxiv, save_metadata

def test_format_name():
    assert format_name("2401.12345") == "2401.12345"
    assert format_name("cs/9912017") == "cs_9912017"
    assert format_name("CS/9912017") == "cs_9912017"

def test_save_metadata(tmp_path: Path):
    author = Mock()
    author.name = "John Doe"

    paper = Mock()
    paper.entry_id = "http://arxiv.org/abs/123.456v1"
    paper.title = "This wonderful paper"
    paper.authors = [author]
    paper.summary = "This is an abstract"
    paper.published = datetime(2000, 10, 8)

    save_metadata(tmp_path, paper)

    metadata_path = tmp_path / "metadata.json"

    assert metadata_path.exists()

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    assert metadata == {
        "arvix_id": "http://arxiv.org/abs/123.456v1",
        "title": "This wonderful paper",
        "authors": ["John Doe"],
        "abstract": "This is an abstract",
        "published": "2000-10-08T00:00:00"
    }

@patch("research_assistant.download.urlretrieve")
@patch("research_assistant.download.arxiv.Client")
def test_download_arxiv(mock_client_cls, mock_urlretrieve, tmp_path: Path):
    # Creates a paper Mock
    paper = Mock()
    paper.entry_id = "http://arxiv.org/abs/2401.12345v1"
    paper.get_short_id.return_value = "2401.12345"
    paper.pdf_url = "https://example.com/test.pdf"
    paper.title = "Test Paper"
    paper.summary = "This is an abstract"
    paper.published = datetime(2000, 10, 8)

    author = Mock()
    author.name = "John Doe"
    paper.authors = [author]

    # Creates a mock client instance
    mock_client = Mock()
    mock_client.results.return_value = [paper]
    mock_client_cls.return_value = mock_client

    assert download_arxiv(tmp_path, max_results=1) == 1

    target_out_dir = Path(tmp_path/ "2401.12345")

    mock_urlretrieve.assert_called_once_with(
        "https://example.com/test.pdf",
        target_out_dir / "paper.pdf"
    )

    metadata = target_out_dir / "metadata.json"
    assert metadata.exists()

    with metadata.open() as f:
        data = json.load(f)

    assert data["title"] == "Test Paper"

@patch("research_assistant.download.urlretrieve")
@patch("research_assistant.download.arxiv.Client")
def test_download_arxiv(mock_client_cls, mock_urlretrieve, tmp_path: Path):
    # Creates a paper Mock
    paper = Mock()
    paper.entry_id = "http://arxiv.org/abs/2401.12345v1"
    paper.get_short_id.return_value = "2401.12345"
    paper.pdf_url = "https://example.com/test.pdf"
    paper.title = "Test Paper"
    paper.summary = "This is an abstract"
    paper.published = datetime(2000, 10, 8)

    author = Mock()
    author.name = "John Doe"
    paper.authors = [author]

    # Creates a mock client instance
    mock_client = Mock()
    mock_client.results.return_value = [paper]
    mock_client_cls.return_value = mock_client

    assert download_arxiv(tmp_path, max_results=1) == 1

    target_out_dir = Path(tmp_path/ "2401.12345")

    mock_urlretrieve.assert_called_once_with(
        "https://example.com/test.pdf",
        target_out_dir / "paper.pdf"
    )

    metadata = target_out_dir / "metadata.json"
    assert metadata.exists()

    with metadata.open() as f:
        data = json.load(f)

    assert data["title"] == "Test Paper"

@patch("research_assistant.download.urlretrieve")
@patch("research_assistant.download.arxiv.Client")
def test_download_fail(mock_client_cls, mock_urlretrieve, tmp_path: Path):
    # Creates a paper Mock
    paper = Mock()
    paper.get_short_id.return_value = "1234.5423"
    paper.pdf_url = "https://example.com/test.pdf"

    # Creates a mock client instance
    mock_client = Mock()
    mock_client.results.return_value = [paper]
    mock_client_cls.return_value = mock_client

    mock_urlretrieve.side_effect = HTTPError(
        url = paper.pdf_url,
        code = 404,
        msg = "Not Found",
        hdrs=None,
        fp=None
    )

    download_arxiv(tmp_path, max_results=1)
    
    # Check the directory was deleted
    assert not (tmp_path / "1234.5678").exists()
