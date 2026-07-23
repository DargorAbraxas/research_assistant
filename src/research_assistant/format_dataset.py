import json
import random
from pathlib import Path
from typing import Any

CONFIDENCE_THRES = 0.8

'''
read all - count dirs
take 10% for validation - should be not 10% of questions, but 10% of papers <--- randomly
make both train and validation  
'''

'''
count all dirs
divide in 2 lists
iterate both and make train/validation
--For each, make a JSON row with the sample
'''

def split_sets(data_dir: Path, train_ratio: float = 0.9, seed: int = 42) -> tuple[list[Path], list[Path]]:
    directories = [dir for dir in data_dir.iterdir() if dir.is_dir()]

    rng = random.Random(seed)
    rng.shuffle(directories)

    split_idx = int(len(directories) * train_ratio)

    train_dirs = directories[:split_idx]
    val_dirs = directories[split_idx:]

    return train_dirs, val_dirs

def format_messages(content: str, question: str, answer: str) -> str:
    return {       
        "messages":[
            {
                "role": "user",
                "content": f"Answer the question about the following section of a paper.\n\nPaper section:\n{content}\n\nQuestion:\n{question}"
            },
            {
                "role": "assistant",
                "content": f"{answer}"
            },
        ]
    }

def format_entries(entries: dict[str: str | list[str: Any]], confidence_thres: float = CONFIDENCE_THRES) -> list[dict[str: Any]]:
    if entries["responses"][0]["question"] == "Error in generation": # File generation had an error
        return None

    return [
        format_messages(entries["section_content"], response["question"], response["answer"])
        for response in entries["responses"]
        if response["confidence"] > confidence_thres
    ]
            
def process_split(dir_set: list[Path], output_file: Path):
    with output_file.open("w") as output:
        for dir in dir_set:
            for json_file in dir.glob("*.json"):
                with json_file.open() as source_file:
                    data = json.load(source_file)

                entries = format_entries(data)
                if entries:
                    for entry in entries:
                        output.write(json.dumps(entry) + "\n")

def format_json_db(raw_data_dir: Path, output_dir: Path) -> None:
    train_dirs, val_dirs = split_sets(raw_data_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    train_output = output_dir / "train.jsonl"
    process_split(train_dirs, train_output)

    val_output = output_dir / "val.jsonl"
    process_split(val_dirs, val_output)
