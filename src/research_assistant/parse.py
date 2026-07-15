import research_assistant.layout_patch
import pymupdf4llm
import json
import re
from pathlib import Path

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

from enum import Enum

class State(Enum):
    NORMAL = 0
    TABLE = 1
    TABLE_CAPTION = 2
    FIGURE_CAPTION = 3
    PICTURE = 4

class MarkdownCleaner:
    def __init__(self):
        self.page_number_re = re.compile(r"^\d+$")
        self.table_header_re = re.compile(r"^\|.*\|$")
        self.table_separator_re = re.compile(r"^\|[-:| ]+\|$")
        self.table_caption_re = re.compile(r"^(?:table)\s+(?:\d+|[IVXLCDM]+)[.:]?", re.IGNORECASE)
        self.figure_caption_re = re.compile(r"^\**(?:Figure|Fig\.?)\**\s*\d+[.:]?", re.IGNORECASE)
        self.figure_text_start_re = re.compile(r"<!-+\s*Start of picture text\s*-+>.*?", re.DOTALL | re.IGNORECASE)
        self.figure_text_end_re = re.compile(r"<!-+\s*End of picture text\s*-+>.*?", re.DOTALL | re.IGNORECASE)
        self.state = State.NORMAL

    def emit(self, output, line):
        if output and output[-1].endswith(" "):
            output[-1] += line.lstrip()
        else:
            output.append(line)

    def clean(self, markdown:str) ->  str:
        output = []

        previous_blank = False

        inside_picture = False
        inside_table = False
        inside_table_caption = False
        inside_figure_caption = False

        for line in markdown.splitlines():

            stripped = line.strip()

            # Picture blocks
            if self.figure_text_start_re.search(stripped):
                inside_picture = True
                continue

            if inside_picture:
                print(f"Inside picture {stripped}")
                if self.figure_text_end_re.search(stripped):
                    inside_picture = False
                print(f"Flag {inside_picture}")
                continue

            
            # Page numbers
            if self.page_number_re.fullmatch(stripped):
                continue

            # Markdown tables
            if self.table_header_re.match(stripped):
                inside_table = True

                # If sentence is interrupted, join the next ommited line
                if output and output[-1]:
                    output[-1] = output[-1].rstrip() + " "
                continue

            if inside_table:
                if not stripped.startswith("|"):
                    inside_table = False
                else:
                    continue

            # Table captions
            if self.table_caption_re.match(stripped):
                inside_table_caption = True

                if output and output[-1]:
                    output[-1] = output[-1].rstrip() + " "
                continue

            if inside_table_caption:
                # Caption ended?
                if (stripped == "" or stripped != stripped.upper()):
                    inside_table_caption = False
                else:
                    continue

            # Figure captions
            if self.figure_caption_re.match(stripped):
                inside_figure_caption = True

                if output and output[-1]:
                    output[-1] = output[-1].rstrip() + " "
                continue

            if inside_figure_caption:
                if stripped == "":
                    inside_figure_caption = False
                continue

            # Blank lines
            if stripped == "":
                if previous_blank:
                    continue

                previous_blank = True
                output.append("")
                continue

            previous_blank = False

            # Keep normal text
            output.append(line)

        return "\n".join(output)
    
def trying():
    filename = "data/2606.24523v1"
    md = pymupdf4llm.to_markdown(f"{filename}.pdf", header=False, footer=False, table_strategy=None, ignore_images=True)

    cleaner = MarkdownCleaner()
    data = cleaner.clean(md)
    Path(f"{filename}_parsed_class.md").write_bytes(data.encode())

trying()
