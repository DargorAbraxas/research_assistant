from ollama import chat
from ollama import ChatResponse
from pathlib import Path
from pydantic import BaseModel, ValidationError
from tqdm import tqdm
from typing import Any
import json
import time

# Ollama structured output
class ConfidenceResponse(BaseModel):
    question: str
    answer: str
    confidence: float

class Responses(BaseModel):
    responses: list[ConfidenceResponse]

class EmptyPrompt(BaseModel):
    prompt_name: str
    empty_prompt: str

class FilledPrompt(BaseModel):
    prompt_name: str
    filled_prompt: str

class SectionPrompts(BaseModel):
    section_content: str
    filled_prompts: list[FilledPrompt]

class OutputResponses(BaseModel):
    section_content: str
    responses: list[ConfidenceResponse]
    

def get_prompts() -> dict[str: list[EmptyPrompt]]:
    '''
    Read the prompts and return a dict in the form
    {"section_name": [(prompt_name, raw_prompt), (prompt_name, raw_prompt), ...]}
    Note that the prompts are the contents of the file, not the file paths
    '''
    prompts_dir = Path(__file__).resolve().parents[1].joinpath("research_assistant", "prompts", "dataset_generation")

    prompts = {
        section_prompt_dir.name: [
            EmptyPrompt(
                prompt_name = file_name.stem,
                empty_prompt = file_name.read_text()
            )
            for file_name
            in section_prompt_dir.glob("*.txt")
        ]
        for section_prompt_dir in prompts_dir.iterdir()
        if section_prompt_dir.is_dir() # only get the prompts inside directories
    }

    return prompts

def load_paper_info(paper_dir: Path) -> tuple[dict[str: Any], dict[str: Any]]:
    paper_json = json.loads((paper_dir / "paper.json").read_text())
    sections_json = json.loads((paper_dir / "standardized.json").read_text())
    return paper_json, sections_json

def get_section_data(paper_json: dict[str, Any], sections_json: dict[str, Any], section: str) -> str:
    # List of original section names correspoding to standardized section naming
    standardized_sections = sections_json["sections"]
    original_section_names = [
        item["original_section"]
        for item in standardized_sections
        if section in item["canonical_sections"]
    ]

    # Match original section names to actual section content
    paper_content = paper_json["sections"]
    section_content = [
        section["content"]
        for section in paper_content
        if section["title"] in original_section_names
    ]

    if section_content:
        return "\n\n".join(section_content)
    return None

def fill_prompts(section_data: str, prompts: list[EmptyPrompt]) -> list[FilledPrompt]:
    # read header
    header = Path(__file__).resolve().parents[1].joinpath("research_assistant", "prompts", "dataset_generation", "header.txt").read_text()

    # read response format
    response_format = Path(__file__).resolve().parents[1].joinpath("research_assistant", "prompts", "dataset_generation", "response_format.txt").read_text()

    filled_prompts = [
        FilledPrompt(
            prompt_name=prompt.prompt_name,
            filled_prompt=prompt.empty_prompt.format(header = header, response_format = response_format, section = section_data)
        )
        for prompt in prompts
    ]
    
    return filled_prompts

def populate_prompts(paper_json: dict[str: Any], sections_json: dict[str: Any], prompts:dict[str: list[EmptyPrompt]]) -> dict[str, SectionPrompts]:
    output = {}

    for section_name, empty_prompts in prompts.items():
        section_data = get_section_data(paper_json, sections_json, section_name)
        if not section_data:
            continue

        output[section_name] = SectionPrompts(
            section_content = section_data,
            filled_prompts = fill_prompts(section_data, empty_prompts)
        )
        
    return output

def call_llm(prompt: str, model_name: str = "qwen3.5:4b", MAX_RETRIES: int = 3) -> Responses:
    for attempt in range(MAX_RETRIES):
        time.sleep(0.1)
        try:
            response: ChatResponse = chat(
                model=model_name,
                format=Responses.model_json_schema(),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "num_ctx": 8192,
                    "temperature": 0.8
                }
            )
            return Responses.model_validate_json(response.message.content)
        
        except (ValidationError, Exception) as e:
            if attempt == MAX_RETRIES - 1:
                return Responses(
                    responses=[
                        ConfidenceResponse(
                            question="Error in generation",
                            answer=f"LLM failed {e}",
                            confidence=0.0
                        )
                    ]
                )

def generate(input_dir: Path, output_dir: Path, model_name: str = "qwen3.5:4b", MAX_RETRIES: int = 3) -> None:
    # load the prompts
    empty_prompts: dict[str: list[EmptyPrompt]] = get_prompts()

    for paper_path in tqdm(input_dir.iterdir(), desc="Generating questions"):
        print(f"\nWorking {paper_path.name}")
        paper_json, sections_json = load_paper_info(paper_path) # Get the paper data, raw and corresponding sections
        populated_prompts = populate_prompts(paper_json, sections_json, empty_prompts)

        for paper_section, section_prompts in populated_prompts.items():
            for filled_prompt in section_prompts.filled_prompts:
                response = call_llm(filled_prompt.filled_prompt, model_name, MAX_RETRIES)

                output = OutputResponses(
                    section_content = section_prompts.section_content,
                    responses = response.responses
                )

                output_questions_dir = output_dir / paper_path.name
                output_questions_dir.mkdir(parents=True, exist_ok=True)

                (output_questions_dir / f"{paper_section}_{filled_prompt.prompt_name}.json").write_text(output.model_dump_json(indent=4))
