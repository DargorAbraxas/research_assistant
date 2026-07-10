import pymupdf4llm
import json
import re
from pathlib import Path

def save_json(dict_data, filename):
    with open(filename, "w") as f:
        f.write(dict_data)

def parse():
    # Takes a PDF, makes it a markdown
    filename = "data/llm-as-a-verifier:_a_general-purpose_verification_framework"
    md = pymupdf4llm.to_markdown(f"{filename}.pdf")
    Path(f"{filename}.md").write_bytes(md.encode())


def remove_picture_blocks(markdown: str) -> str:
    pattern = (
        r'<!--\s*Start of picture text\s*-->.*?'
        r'<!--\s*End of picture text\s*-->'
    )

    return re.sub(pattern, "", markdown, flags=re.DOTALL | re.IGNORECASE)

def remove_page_numbers(markdown: str) -> str:
    pattern = r'\n\s*\d+\s*\n'
    return re.sub(pattern, '\n', markdown)


from collections import Counter

def find_repeated_lines(markdown, min_occurrences=3):
    counter = Counter()
    exclude = [
        lambda s: s.startswith("#"),
        lambda s: s.startswith("```"),
        lambda s: re.fullmatch(r"\|[:\-| ]+\|?", s) is not None
    ]

    exclude_strings = {
        "Introduction"
    }

    lines = [line.strip() for line in markdown.splitlines() if line.strip()]
    counter.update(lines)

    repeated = set()

    for line, count in counter.items():
        if count < min_occurrences:
            continue
        if any(rule(line) for rule in exclude):
            continue

        if line in exclude_strings:
            continue

        repeated.add(line)

    return repeated

def remove_repeated_lines(text, repeated):
    lines = text.splitlines()

    cleaned = [line for line in lines if line.strip() not in repeated]

    return "\n".join(cleaned)

def remove_figure_text(markdown):
    return re.sub(
        r"\n\s*\**(?:Figure|Fig\.?)\**\s*\d+[:.]?.*?(\n\n)",
        " ",
        markdown,
        flags=re.DOTALL | re.IGNORECASE,
    )


def remove_empty_lines(markdown):
    return re.sub(r'(?:\r?\n[ \t]*){2,}', '\n\n', markdown) # It might have tabs or whitespaces and not only empty newlines

    
def split_sections(data):
    pattern = r'^(#{1,6}\s+.+)$'
    matches = list(re.finditer(pattern, data, flags=re.MULTILINE))
    sections = {}

    for i, match in enumerate(matches):
        title = match.group(1).lstrip("#").strip()  

        # Stop if "Appendix" is in the title. Discard everything afterwards
        if "Appendix" in title:
            break

        # Do not add these sections
        if any(non_important in title for non_important in ["Acknowledgments", "References", "Bibliography"]):
            continue

        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(data)
        content = data[start:end].strip()
        sections[title] = content

    return sections


def make_stuff():
    paper = "data/llm-as-a-verifier:_a_general-purpose_verification_framework.md"

    with open(paper, "r") as f:
        data = f.read()

    data = remove_picture_blocks(data)
    data = remove_page_numbers(data)

    repeated = find_repeated_lines(data)
    data = remove_repeated_lines(data, repeated)

    data = remove_figure_text(data)
    data = remove_empty_lines(data)

    sections = split_sections(data)
    

    print(sections.keys())
    print("****")
    print(sections[list(sections.keys())[1]])
    return sections

make_stuff()
