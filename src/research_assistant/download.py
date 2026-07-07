import arxiv
from urllib.request import urlretrieve
from urllib import error

def format_title(title: str):
    '''
    Format the title: remove spaces and move all to lower to keep it standard
    '''
    title = title.replace(" ", "_")
    title = title.lower()
    return title

def download_arxiv(max_results=2000):
    '''
    Download papers from ArXiv. 2000 paper by default
    '''

    # Construct the default API client.
    client = arxiv.Client()

    # Search files on ArXiv
    search = arxiv.Search(
        query="(cat:cs.AI OR cat:cs.CL) AND LLM",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    results = client.results(search)


    for paper in results:
        title = format_title(paper.title)
        try:
            urlretrieve(paper.pdf_url, f"data/{title}.pdf")
        except error.HTTPError as e:
            print(f"HTTP error: {e}")
            
download_arxiv(2)
