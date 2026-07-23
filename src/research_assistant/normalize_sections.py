from ollama import chat
from ollama import ChatResponse
from pathlib import Path
from pydantic import BaseModel
from tqdm import tqdm

CANONICAL_SECTIONS = [
    "title",
    "abstract",
    "introduction",
    "related_work",
    "method",
    "results",
    "discussion",
    "limitations",
    "future_work",
    "conclusion",
    "appendix",
    "other"
]

# Ollama json answer
class Section(BaseModel):
    original_section: str
    canonical_sections: list[str]
    confidence: float
    reason: str

class Sections(BaseModel):
    sections: list[Section]

def fill_prompt(paper_text: str) -> str:
    prompt_path = Path(__file__).resolve().parents[1].joinpath("research_assistant", "prompts", "normalize_sections.txt")
    prompt = prompt_path.read_text()

    # Make list with possible sections
    sections_str = "".join([f" - {section}\n" for section in CANONICAL_SECTIONS])

    # Fill loaded prompt string
    return prompt.format(labels=sections_str, paper=paper_text)

def call_llm(prompt: str, model_name: str = "qwen3.5:4b") -> Sections:
    response: ChatResponse = chat(
        model=model_name,
        format=Sections.model_json_schema(),
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ],
        options={
            "num_ctx": 32768, #131072, <---- Change if needed. This is the max context len
            "temperature": 0
        },
        # think=False
    )

    return Sections.model_validate_json(response.message.content)

def normalize_sections(files_path: Path, model_name: str = "qwen3.5:4b") -> None:
    for paper_path in tqdm(files_path.glob("**/paper.json"), desc="Querying LLM"):
        filled_prompt = fill_prompt(paper_path.read_text())
        normalized_sections = call_llm(filled_prompt, model_name)

        output_path = Path(paper_path.parent / "standardized.json")
        output_path.write_text(normalized_sections.model_dump_json(indent=4))
