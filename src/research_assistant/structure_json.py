import json
import re
from pathlib import Path
from tqdm import tqdm

def add_from_metadata(paper_dir: Path, output_dict: dict) -> dict[str: str | list[str]]:
    metadata_keys = ["arvix_id", "title", "authors"]
    metadata_path = list(paper_dir.glob("*.json"))[-1]
    metadata = json.load(metadata_path.open())

    # Populate relevant metadata
    output_dict["metadata"] = {
        meta_key: meta_data for meta_key, meta_data in metadata.items() if meta_key in metadata_keys
    }

    # Populate abstract
    output_dict["abstract"] = {
        "content": metadata["abstract"]
    }

    return output_dict

def start_parsing(line: str, output_dic: dict[str: str | list[str]]) -> bool:
    '''
    Some papers do not include their abstract preceded with the heading "Abstract". For those edge cases,
    this function checks for the actual content of the abstract, extracted from the metadata. As this is also
    inconsistent, it checks for the first sentence of the abstract as a best effort.
    '''
    if "Abstract" in line:
        return True
    
    abstract_content = output_dic["abstract"]["content"].split(".")[0]
    if abstract_content.strip() in line:
        return True
    return False

def add_sections(paper_dir: Path, output_dic: dict[str: str | list[str]]) -> dict[str: str | list[str]] | None:
    paper_path = list(paper_dir.glob("*.md"))[-1]
    paper_md = paper_path.read_text()

    HEADING_PATTERN = re.compile(r"^(#{2})\s+(.*)$")

    sections = []
    current_section = None

    start_adding = False
    for line in paper_md.splitlines():
        if not start_adding:
            start_adding = start_parsing(line, output_dic)
            continue
        
        else:
            match = HEADING_PATTERN.match(line)

            if match:
                if current_section is not None:
                    current_section["content"] = current_section["content"].strip()
                    sections.append(current_section)

                hashes, title = match.groups()

                current_section = {
                    "level": len(hashes),
                    "title": title.strip(),
                    "content": ""
                }

            else:
                if current_section is None:
                    continue
                if line:
                    current_section["content"] += line.strip() + "\n\n"

    # Save last section
    if current_section is not None:
        current_section["content"] = current_section["content"].strip()
        sections.append(current_section)

    # Check section length. If too long, signal of problem parsing:
    if len(sections) > 9:
        return None

    output_dic["sections"] = sections
    return output_dic


def structure_json(paper_dir: Path) -> dict[str: str | list[str]]:
    output_dict = {}
    
    output_dict = add_from_metadata(paper_dir, output_dict)
    output_dict = add_sections(paper_dir, output_dict)

    return output_dict

def parse_md_json(download_dir: Path, json_path: Path) -> None:
    # Use directory. Internal functions search for metadata.json and paper.md
    for dir in tqdm(download_dir.iterdir(), desc="Parsing to json"):
        json_dict = structure_json(dir)

        if json_dict:
            file_path = Path(json_path / dir.name / "paper.json")
            # Make sure the destination directory exists or create it
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with file_path.open("w") as f:
                json.dump(json_dict, f, indent=4)
