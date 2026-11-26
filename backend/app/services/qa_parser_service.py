"""
Extracts {question, reference_answer, one_liner} triples from a note's
"Interview Q&A" section.

Format is consistent across the vault regardless of the heading's number
prefix (e.g. "## 9. Interview Q&A" in LLM Engineering notes, "## 7. Interview
Q&A" in Deep Learning course notes): a '## ' heading containing the phrase
"Interview Q&A", followed by repeated

    **Q: <question>**
    A: <answer, one or more paragraphs>

    *One-liner: <compressed takeaway>*

blocks, ending at the next '## ' heading or end of file.
"""
import re
from typing import List, Optional, TypedDict

_HEADING_RE = re.compile(r"^##\s+.*Interview Q\s*&\s*A.*$", re.MULTILINE | re.IGNORECASE)
_NEXT_HEADING_RE = re.compile(r"^##\s", re.MULTILINE)

_QA_BLOCK_RE = re.compile(
    r"\*\*Q:\s*(?P<question>.+?)\*\*\s*\n"
    r"A:\s*(?P<answer>.*?)\n\s*\n"
    r"\*One-liner:\s*(?P<one_liner>.+?)\*",
    re.DOTALL,
)


class QAPair(TypedDict):
    question: str
    reference_answer: str
    one_liner: str


def _extract_qa_section(note_content: str) -> Optional[str]:
    """Return the body text between the Interview Q&A heading and the next
    '## ' heading (or end of file), or None if no such heading exists."""
    heading_match = _HEADING_RE.search(note_content)
    if not heading_match:
        return None

    start = heading_match.end()
    next_heading_match = _NEXT_HEADING_RE.search(note_content, pos=start)
    end = next_heading_match.start() if next_heading_match else len(note_content)
    return note_content[start:end]


def extract_qa_pairs(note_content: str) -> List[QAPair]:
    """Parse all Q&A pairs out of a note's Interview Q&A section.

    Returns an empty list if the note has no such section, or if the
    section exists but doesn't match the expected block format — this is a
    pure, best-effort extraction, never raises on unexpected content.
    """
    body = _extract_qa_section(note_content)
    if body is None:
        return []

    return [
        QAPair(
            question=match.group("question").strip(),
            reference_answer=match.group("answer").strip(),
            one_liner=match.group("one_liner").strip(),
        )
        for match in _QA_BLOCK_RE.finditer(body)
    ]
