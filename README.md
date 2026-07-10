# Description

This is a simple research assistant. It handles the downloading of files, from [ArXiv](https://arxiv.org/), then parsing the PDF files and generating data. Afterwards, uses the data to train a LLM to make it a better assistant.

To install, run

```bash
uv sync
```

ToComplete

## Download files

The project counts with different scripts for each step. By default, the script to download files fetches 1000 research papers regarding LLMs. Feel free to modify it to download more/less files. 

To get the papers, run:

```py
uv run scripts/download_data.py 
```
