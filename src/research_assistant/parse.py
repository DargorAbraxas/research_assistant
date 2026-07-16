import research_assistant.layout_patch
import pymupdf4llm
import json
import re
from pathlib import Path

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

from enum import Enum, auto

class State(Enum):
    NORMAL = auto()
    TABLE = auto()
    TABLE_CAPTION = auto()
    FIGURE_CAPTION = auto()
    PICTURE = auto()

class MarkdownCleaner:
    def __init__(self):
        self.page_number_re = re.compile(r"^\d+$")
        self.table_header_re = re.compile(r"^\|.*\|$")
        self.table_separator_re = re.compile(r"^\|[-:| ]+\|$")
        self.table_caption_re = re.compile(r"^(?:table)\s+(?:\d+|[IVXLCDM]+)[.:]?", re.IGNORECASE)
        self.figure_caption_re = re.compile(r"^\**(?:Figure|Fig\.?)\**\s*\d+[.:]?", re.IGNORECASE)
        self.figure_text_start_re = re.compile(r"<!-+\s*Start of picture text\s*-+>.*?", re.DOTALL | re.IGNORECASE)
        self.figure_text_end_re = re.compile(r"<!-+\s*End of picture text\s*-+>.*?", re.DOTALL | re.IGNORECASE)

    def emit(self, output: list[str], line: str, join_with_previous: bool) -> bool:
        """
        Append a line while automatically joining text that
        was split by a removed block.
        """
        
        line = line.lstrip()
        if line.endswith(" ") and not line.startswith("#"):
            join_with_previous = True
  
        if join_with_previous and output:
            if output[-1] == "":
                output[-1] = line    
                return False

            output[-1] = output[-1].rstrip() + " " + line
            return False
        

        output.append(line)
        return join_with_previous

    def should_join_next_line(self, output: list[str]) -> bool:
        if not output:
            return False

        last = output[-1].rstrip()

        if not last:
            return False

        # Finished a sentence
        if last.endswith((".", "!", "?", ":", ";")):
            return False

        # Previous is heading
        if last.startswith("#"):
            return False
        
        # Bullets
        if re.match(r"^\s+[-*+] ", last):
            return False

        # Numbered lists
        if re.match(r"^\d+\.", last):
            return False

        return True

    def clean(self, markdown:str) -> str:
        previous_blank = False
        join_with_previous = False
        state = State.NORMAL
        output = []

        # Handle parser states
        for line in markdown.splitlines():

            stripped = line.strip()

            # ================
            # NORMAL STATE
            # ================
            if state == State.NORMAL:
                # Picture blocks
                if self.figure_text_start_re.search(stripped):
                    state = State.PICTURE
                    continue
                
                # Page numbers
                if self.page_number_re.fullmatch(stripped):
                    continue

                # Remove corresponding author
                if "Corresponding author" in stripped:
                    join_with_previous = self.should_join_next_line(output)
                    continue

                # Markdown tables
                if self.table_header_re.match(stripped):
                    state = State.TABLE
                    join_with_previous = self.should_join_next_line(output)
                    continue
            
                # Table captions
                if self.table_caption_re.match(stripped):
                    state = State.TABLE_CAPTION
                    join_with_previous = self.should_join_next_line(output)
                    continue

                # Figure captions
                if self.figure_caption_re.match(stripped):
                    state = State.FIGURE_CAPTION
                    join_with_previous = self.should_join_next_line(output)
                    continue

                # Blank lines
                if stripped == "":
                    if previous_blank or join_with_previous:
                        continue

                    previous_blank = True
                    output.append("")
                    continue

                previous_blank = False
                join_with_previous = self.emit(output, line, join_with_previous)

            # ================
            # IN PICTURE
            # ================
            elif state == State.PICTURE:
                if self.figure_text_end_re.search(stripped):
                    state = State.NORMAL

            # ================
            # IN TABLE
            # ================
            elif state == State.TABLE:
                # End of table?
                if not stripped.startswith("|"):
                    state = State.NORMAL

                    # Add the line table finished
                    if stripped:
                        join_with_previous = self.emit(output, line, join_with_previous)

            # ================
            # IN TABLE CAPS
            # ================
            elif state == State.TABLE_CAPTION:
                # Caption ended?
                if (stripped == "" or stripped != stripped.upper()):
                    state = State.NORMAL

                    # Add the line caption finished
                    if stripped:
                        join_with_previous = self.emit(output, line, join_with_previous)

            # ================
            # IN FIGURE CAPS
            # ================
            elif state == State.FIGURE_CAPTION:
                if stripped == "":
                    state = State.NORMAL

        return "\n".join(output)
    
def trying():
    # filename = "data/2606.24523v1"
    filename = "data/2606.25445v1"
    md = pymupdf4llm.to_markdown(f"{filename}.pdf", header=False, footer=False, table_strategy=None, ignore_images=True)
    Path(f"{filename}_base.md").write_bytes(md.encode())

    cleaner = MarkdownCleaner()
    data = cleaner.clean(md)
    Path(f"{filename}_parsed_class.md").write_bytes(data.encode())

trying()
