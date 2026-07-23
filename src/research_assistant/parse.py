import research_assistant.layout_patch
import pymupdf4llm
import re
from pathlib import Path
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
        self.table_caption_re = re.compile(r"^\**(?:table)\s+(?:\d+|[IVXLCDM]+)[.:]?", re.IGNORECASE)
        self.figure_caption_re = re.compile(r"^\**(?:Figure|Fig\.?)\s*\d+\**[.:]+", re.IGNORECASE) ##
        self.figure_text_start_re = re.compile(r"<!-+\s*Start of picture text\s*-+>.*?", re.DOTALL | re.IGNORECASE)
        self.figure_text_end_re = re.compile(r"<!-+\s*End of picture text\s*-+>.*?", re.DOTALL | re.IGNORECASE)
        self.ending_superscript = re.compile(r"<sup>\d+<\/sup>\s*$")
        self.keywords_re = re.compile(r"^\**_*(?:Keywords)[.:]*", re.DOTALL | re.IGNORECASE)
        self.paragraph_figure_caption_re = re.compile(r"\*+(?:Figure|Fig\.?)\s*\d+.*$", re.DOTALL)

        break_sections = ["Appendix", "Acknowledgement", "Acknowledgment", "References", "Bibliography"]
        self.break_parsing_re = re.compile(rf"^#+\s+\**(?:{'|'.join(break_sections)})", re.IGNORECASE)

    def break_parsing(self, line: str) -> bool:
        pass

    def is_metadata_line(self, line: str) -> bool:
        line = line.strip()

        # Markdown blockquote
        if line.startswith(">"):
            return True
        
        # Keywords line
        if self.keywords_re.match(line):
            return True

        # Typical affiliation markers
        if re.match(r"^_?[†‡0-9]+", line):
            return True

        # Email addresses
        if "@" in line:
            return True

        return False
    
    def emit(self, output: list[str], line: str, join_with_previous: bool) -> bool:
        """
        Append a line while automatically joining text that
        was split by a removed block.
        """
        
        line = line.lstrip()

        if line.startswith("#"):
            if join_with_previous:
                line = "\n" + line

            output.append(line)
            return False    
  
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

        # Don't join after blockquotes (often affiliations/quotes)
        if last.startswith(">") or self.ending_superscript.search(last):
            return False
        
        if re.search(r"\.?\*+\s*$", last):
            return False

        # Don't join after fully italic metadata lines
        if self.is_metadata_line(last):
            return False

        if not last:
            return False

        # Finished a sentence
        if last.endswith((".", "!", "?", ":")):
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

            # Stop if breaking header is reached
            if self.break_parsing_re.match(stripped):
                break
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
                    continue
            
                # Table captions
                if self.table_caption_re.match(stripped):
                    state = State.TABLE_CAPTION
                    join_with_previous = self.should_join_next_line(output)
                    continue

                # Figure captions
                if self.figure_caption_re.match(stripped):
                    state = State.FIGURE_CAPTION
                    continue

                # Do not add email metadata
                if stripped.startswith(">"):
                    continue

                # Incorrect figure caption in text
                line = self.paragraph_figure_caption_re.sub("", line)

                # Blank lines
                if stripped == "":
                    if previous_blank or join_with_previous:
                        continue

                    previous_blank = True
                    join_with_previous = self.should_join_next_line(output)
                    if not join_with_previous:
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
                        join_with_previous = self.emit(output, stripped, join_with_previous)

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

def parse_data(download_path: Path):
    for doc in download_path.glob("**/*.pdf"):
        markdown = pymupdf4llm.to_markdown(doc, header=False, footer=False, table_strategy=None, ignore_images=True)
        
        cleaner = MarkdownCleaner()
        clean_markdown = cleaner.clean(markdown)
        Path(doc.parent / "paper.md").write_bytes(clean_markdown.encode())
