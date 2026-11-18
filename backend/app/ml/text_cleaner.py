"""Resume text cleaning, artifact removal, deduplication, and PII redaction."""

import re
import unicodedata
from typing import List

LIGATURE_MAP = {
    "\ufb00": "ff",
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u00a0": " ",
}

BULLET_PATTERN = re.compile(r"^[\s\u2022\u2023\u25e6\u2043\u2219\u25aa\u25cf\u25cb\-\*•▪◦●]+")
CONTROL_CHARS_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
WEIRD_SYMBOLS_PATTERN = re.compile(r"[^\w\s.,;:/()+\-#@&%|'\"!?]")
PAGE_NUMBER_PATTERN = re.compile(r"^(?:page\s*\d+(?:\s*of\s*\d+)?|\d+\s*/\s*\d+)$", re.IGNORECASE)

EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_REGEX = re.compile(
    r"(?<!\d)(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})(?!\d)"
)


def clean_resume_text(raw_text: str) -> str:
    """Clean extracted resume text by stripping artifacts, normalizing whitespace, and removing duplicates."""
    if not raw_text:
        return ""

    text = unicodedata.normalize("NFKC", raw_text)
    for src, dst in LIGATURE_MAP.items():
        text = text.replace(src, dst)

    # Remove non-printable control characters and unify line endings
    text = CONTROL_CHARS_PATTERN.sub("", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    cleaned_lines: List[str] = []
    seen_exact_lines: set[str] = set()
    prev_normalized = ""

    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue

        # Drop standalone page number artifacts (e.g., "Page 1 of 2")
        if PAGE_NUMBER_PATTERN.match(line):
            continue

        # Normalize leading bullets to a clean dash
        had_bullet = bool(BULLET_PATTERN.match(line)) and not line[0].isalnum()
        line = BULLET_PATTERN.sub("", line).strip() if had_bullet else line

        # Remove stray non-standard glyph artifacts while preserving technical tokens (C++, C#, Node.js, @)
        line = WEIRD_SYMBOLS_PATTERN.sub(" ", line)
        line = re.sub(r"[ \t]{2,}", " ", line).strip()

        if not line:
            continue

        if had_bullet:
            line = f"- {line}"

        # Deduplicate consecutive identical lines and repeated multi-word header/footer lines
        normalized_key = re.sub(r"\s+", " ", line).lower()
        if normalized_key == prev_normalized:
            continue
        if len(normalized_key) > 20 and normalized_key in seen_exact_lines:
            continue

        seen_exact_lines.add(normalized_key)
        prev_normalized = normalized_key
        cleaned_lines.append(line)

    result = "\n".join(cleaned_lines)
    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    return result


def redact_pii(text: str) -> str:
    """Mask emails and phone numbers so evidence snippets never leak personal contact details."""
    if not text:
        return ""
    redacted = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
    redacted = PHONE_REGEX.sub("[REDACTED_PHONE]", redacted)
    return redacted


def mask_email(email: str) -> str:
    """Return a privacy-preserving masked email (e.g., a***@example.com)."""
    if "@" not in email:
        return "[REDACTED_EMAIL]"
    local, domain = email.split("@", 1)
    prefix = local[0] if local else "*"
    return f"{prefix}***@{domain}"


def mask_phone(phone: str) -> str:
    """Return a privacy-preserving masked phone number keeping only the last 2 digits."""
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 4:
        return "***"
    return f"***-***-**{digits[-2:]}"
