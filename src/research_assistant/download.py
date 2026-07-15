import arxiv
from tqdm import tqdm
from pathlib import Path
from urllib import error
from urllib.request import urlretrieve

def format_name(short_id: str) -> str:
    '''
    Format the ID: remove slashes and move all to lower to keep it standard
    '''
    short_id = short_id.replace("/", "_")
    short_id = short_id.lower()
    return short_id

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
        query="(cat:cs.AI OR cat:cs.CL) AND LLM AND NOT Poster",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    results = client.results(search)
    # Keep track of successfully downloaded papers
    successes = 0

    for paper in tqdm(results, desc="Downloading papers"):
        short_id = format_name(paper.get_short_id())
        try:
            urlretrieve(paper.pdf_url, output_dir / f"{short_id}.pdf")
            successes += 1
        except error.HTTPError as e:
            print(f"HTTP error: {e}")
    
    print(f"Downloaded {successes} papers.")
    return successes
