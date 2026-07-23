# Description

This is a simple research assistant. It handles the downloading of files, from [ArXiv](https://arxiv.org/), then parsing the PDF files and generating data. Afterwards, uses the data to train a LLM to make it a better assistant.

The following `uv` command will install all the required dependencies for this project. The only addition is [Ollama](https://ollama.com/), which allows running LLMs easily. LLMs are used to normalize data and generate the training dataset. Make sure to follow the instructions in their webpage to install it.

To install this project, run

```bash
uv sync
```


## Download files

The project counts with different scripts for each step. By default, the script to download files fetches 1000 research papers regarding LLMs. Feel free to modify it to download more/less files. 

To get the papers, run:

```py
uv run scripts/download_data.py 
```

Inside the script, you can change the default path where the data is saved.

## Markdown parsing

After downloading the papers, multiple PDFs must be processed to be read by a model. The format of papers is **not** standard, so reading these into raw text is a non-trivial task. To convert the PDFs into markdown, using some heuristics, run

```py
uv run scripts/parse_data.py 
```

This script will attempt to convert the **text** of the research paper into markdown, preserving the structure. Tables and figures will be discarded. Formulas cannot be consistently converted into markdown. If needed, other methods based on image processing can be used.

## JSON parsing

Research papers often contain multiple sections with might or might not provide value, while presenting difficulties to deal with (Acknowledgment, Bibliography, etc.). Parsing into structured JSON allows to focus on important parts, and works as a first step towards normalizing the information. To do so, run

```py
uv run scripts/parse_to_json.py 
```

### Normalizing sections

Not all papers use the same sections. Many non-peer-reviewed articles can even have headings that are completely unconventional, making it difficult to classify. Sections need to be normalized in order to classify the information in a consistent way to train models. Some sections might be discarded, while others might refer to the same section, with different naming. Heuristics can be created to map these and achieve a clear organization.

For this, [Ollama](https://ollama.com/) is used. By default, [Qwen 3.5-4B](https://ollama.com/library/qwen3.5:4b) is used. This can be changed if needed and if the configuration of the running computer allows it. To normalize the `json` files, run

```py
uv run scripts/normalize_structures.py 
```

## Data generation

Using the structured papers, pairs of question/answer can be generated. By default, [Qwen 3.5-4B](https://ollama.com/library/qwen3.5:4b) is used, which can be switched easily by any other model Ollama allows. Inside `src/research_assistant/prompts` are multiple prompts used to generate questions based on each of the normalized sections of the papers, generated in the previous step. These prompts can be modified, removed, or more can be added by only adding new `txt` files with the appropriate format. Take a look at the files if you want to add more prompts.

To generate data from structured papers, run

```py
uv run scripts/generate_dataset.py 
```

### Dataset format

Once the questions are generated, the output files must be formatted as a language modeling dataset, in [conversational format](https://huggingface.co/docs/trl/main/en/dataset_formats#language-modeling). Also, the source section must be included to give the LLM enough context to learn something meaningful (i.e., add the `Method` section for questions related to this section). All is done by running

```py
uv run scripts/format_dataset.py 
```

## Fine-tuning the model

Finally, once the data is ready, run the following command to train the model

```py
uv run scripts/train_model.py 
```

By default, [QLoRA](https://huggingface.co/docs/trl/v1.10.0/en/peft_integration#qlora-quantized-low-rank-adaptation) is used to train. Check the source file if you want to change the hyperparameters, if your system allows. It might be particularly encouraging to increase the context length, which could improve the model's learning.

## Metrics
TBD