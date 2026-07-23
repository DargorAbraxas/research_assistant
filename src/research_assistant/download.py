import arxiv
import json
from arxiv import Result
from tqdm import tqdm
from pathlib import Path
from shutil import rmtree
from urllib import error
from urllib.request import urlretrieve

def format_name(short_id: str) -> str:
    '''
    Format the ID: remove slashes to avoid issues creating directories
    '''
    short_id = short_id.replace("/", "_")
    short_id = short_id.lower()
    return short_id

def save_metadata(paper_dir: Path, paper: Result):
    metadata = {
        "arvix_id": paper.entry_id,
        "title": paper.title,
        "authors": [author.name for author in paper.authors],
        "abstract": paper.summary,
        "published": paper.published.isoformat()
    }

    with open(paper_dir / "metadata.json", "w") as json_file:
        json.dump(metadata, json_file, indent=4)

def download_arxiv(output_dir: Path, max_results:int=1000) -> int:
    '''
    Download papers from ArXiv. 1000 paper by default
    '''

    # Make sure the destination directory exists or create it
    output_dir.mkdir(parents=True, exist_ok=True)

    # Construct the default API client.
    client = arxiv.Client()

    # Search files on ArXiv
    search = arxiv.Search(
        query="(cat:cs.AI OR cat:cs.CL) AND LLM ANDNOT (Poster OR Survey)",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    results = client.results(search)
    # Keep track of successfully downloaded papers
    successes = 0

    for paper in tqdm(results, desc="Downloading papers"):
        short_id = format_name(paper.get_short_id())
        try:
            paper_dir = Path(output_dir / short_id)
            paper_dir.mkdir(parents=True, exist_ok=True)
            urlretrieve(paper.pdf_url, paper_dir / "paper.pdf")
            save_metadata(paper_dir, paper)
            successes += 1
        except error.HTTPError as e:
            rmtree(paper_dir)
            print(f"HTTP error: {e}")
    
    print(f"Downloaded {successes} papers.")
    return successes
