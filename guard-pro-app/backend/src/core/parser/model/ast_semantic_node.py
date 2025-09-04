from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ASTSemanticNode:
    """Represents a parsed code chunk with metadata"""

    type: str
    name: str
    content: str
    file_path: str
    line_start: int
    line_end: int
    language: str
    parameters: List[str] = None
    return_type: Optional[str] = None
    imports: List[str] = None
    calls_to: List[str] = None
    parent_class: Optional[str] = None
