import re


def extract_headings(markdown_text: str) -> list[tuple[int, str]]:
    headings = []
    for line in markdown_text.splitlines():
        match = re.match(r"^(#+)\s+(.+?)\s*$", line.strip())
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append((level, text))
    return headings


def normalize_heading(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())