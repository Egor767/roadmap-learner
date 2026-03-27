from enum import Enum


class QuestionStatus(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    REPEAT = "repeat"


class ConceptStatus(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    REPEAT = "repeat"
