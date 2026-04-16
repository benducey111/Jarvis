"""Text processing utilities for the Jarvis TTS pipeline."""

import re


# Characters / markdown to strip before speaking aloud
_STRIP_PATTERNS = [
    (r"\*{1,3}(.*?)\*{1,3}", r"\1"),        # bold / italic markdown
    (r"`{1,3}[^`]*`{1,3}", ""),              # inline code and code blocks
    (r"\[([^\]]+)\]\([^\)]+\)", r"\1"),      # markdown links → link text
    (r"#+\s+", ""),                           # heading markers
    (r"^[-*]\s+", "", re.MULTILINE),         # bullet points
    (r"https?://\S+", ""),                   # bare URLs
]

# Sentence boundary: ends with . ! ? followed by space or end-of-string
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+|(?<=[.!?])$")


def clean_for_tts(text: str) -> str:
    """Strip markdown and technical formatting from text before TTS.

    Args:
        text: Raw AI response possibly containing markdown.

    Returns:
        Cleaned plain-text string suitable for speech synthesis.
    """
    result = text
    for pattern_args in _STRIP_PATTERNS:
        if len(pattern_args) == 3:
            pattern, repl, flags = pattern_args
            result = re.sub(pattern, repl, result, flags=flags)
        else:
            pattern, repl = pattern_args
            result = re.sub(pattern, repl, result)
    return result.strip()


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentence-sized chunks for streaming TTS.

    Tries to split on sentence boundaries (.!?) while keeping
    chunks long enough to sound natural (minimum ~40 chars).

    Args:
        text: Full or partial text string.

    Returns:
        List of sentence strings (may be empty).
    """
    sentences = _SENTENCE_END.split(text.strip())
    return [s.strip() for s in sentences if s.strip()]


def extract_sentence_boundary(buffer: str) -> tuple[str, str]:
    """Given an accumulating text buffer, extract the first complete sentence.

    Args:
        buffer: Accumulating token buffer from streaming AI response.

    Returns:
        (sentence_to_speak, remaining_buffer) — sentence is empty if none found yet.
    """
    match = re.search(r"[.!?]\s", buffer)
    if match:
        end = match.end()
        return buffer[:end].strip(), buffer[end:]
    return "", buffer
