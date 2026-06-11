from pipeline.core.markdown_utils import extract_headings, normalize_heading


def validate_outline(text: str) -> tuple[bool, list[str]]:
    issues = []
    stripped = text.strip()
    if not stripped:
        issues.append("Outline is empty")
    required_markers = ["## Introducción", "## Desarrollo", "## Cierre"]
    for marker in required_markers:
        if marker not in stripped:
            issues.append(f"Missing section: {marker}")
    return (len(issues) == 0, issues)


def validate_draft_against_outline(outline: str, draft: str) -> tuple[bool, list[str]]:
    issues = []
    outline_headings = [(lvl, txt) for lvl, txt in extract_headings(outline) if lvl in (1, 2, 3)]
    draft_headings = [(lvl, txt) for lvl, txt in extract_headings(draft) if lvl in (1, 2, 3)]

    outline_norm = {(lvl, normalize_heading(txt)) for lvl, txt in outline_headings}
    draft_norm = {(lvl, normalize_heading(txt)) for lvl, txt in draft_headings}

    for heading in outline_norm:
        if heading not in draft_norm:
            issues.append(f"Missing heading from outline: level={heading[0]} text={heading[1]}")

    if len(draft.strip()) < 800:
        issues.append("Draft too short; minimum expected length is 800 characters")

    placeholders = ["[TODO]", "<TODO>", "lorem ipsum", "pendiente"]
    lowered = draft.lower()
    for token in placeholders:
        if token.lower() in lowered:
            issues.append(f"Placeholder detected: {token}")

    return (len(issues) == 0, issues)


def validate_edited_draft(original: str, edited: str) -> tuple[bool, list[str]]:
    issues = []
    if not edited.strip():
        issues.append("Edited draft is empty")

    original_headings = {(lvl, normalize_heading(txt)) for lvl, txt in extract_headings(original)}
    edited_headings = {(lvl, normalize_heading(txt)) for lvl, txt in extract_headings(edited)}

    for heading in original_headings:
        if heading not in edited_headings and heading[0] <= 3:
            issues.append(f"Missing heading from original: level={heading[0]} text={heading[1]}")

    if len(edited.strip()) < 800:
        issues.append("Edited draft too short")

    lowered = edited.lower()
    placeholders = ["[todo]", "<todo>", "lorem ipsum", "pendiente"]
    for token in placeholders:
        if token in lowered:
            issues.append(f"Placeholder detected: {token}")

    return (len(issues) == 0, issues)