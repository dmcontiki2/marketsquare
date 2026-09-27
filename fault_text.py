"""FAULT-TEXT-1 (27 Sep 2026, David, closing DW-162).

David's words: "No complaint should allow large amount of characters but only a limited set of
characters, and how can we make it safe of hidden code?"

ONE cleaner for every word a person types into a complaint or a support message. It is used at
BOTH ends, so an old row, an e-mailed complaint or a future door gets the same treatment:
  * at the door  - bea_main.py POST /app/fault and POST /support/message, before anything is stored;
  * at the use   - scripts/maintenance_agent.py, before a complaint reaches a paid AI prompt or a file.

What it does, in order:
  1. Caps the raw input before any work (a huge paste costs nothing to refuse).
  2. NFKC-normalises, so look-alike and full-width characters become their plain form.
  3. Keeps ONLY an allow-list: letters and digits in any language (isiZulu, Afrikaans, Sepedi ...),
     at most two accent marks per letter, spaces, line breaks (message body only) and ordinary
     punctuation . , ; : ! ? ' " ( ) - / & % + @ # * = _ $ and the currency signs.
     Everything else is DROPPED: < > { } [ ] \\ | ` ^ ~ (the characters code and markup are built
     from), control characters, zero-width and right-to-left override characters (the ones used
     to HIDE text), emoji and private-use symbols.
  4. Collapses runs of spaces and blank lines, then cuts to the length limit.

Why this makes hidden code harmless: a web page can only run code that arrives inside < > tags or
a markup link, and neither can be written without the dropped characters. Hidden text needs
zero-width or direction-override characters, which are dropped too. What is left is plain words.
The AI prompts additionally fence the complaint as DATA (see maintenance_agent._fence), so words
that try to give the AI orders are read as a complaint, not obeyed.
"""
import re
import unicodedata

TITLE_MAX = 150      # the one-line headline
DETAIL_MAX = 1000    # the whole message, about 150-200 words
NAME_MAX = 80        # a person's name

_PUNCT = set(" .,;:!?'\"()-/&%+@#*=_$€£¥‘’“”–—…")
_RAW_CAP_FACTOR = 4  # look at no more than 4x the limit of raw input


def _keep(ch: str) -> bool:
    if ch in _PUNCT:
        return True
    cat = unicodedata.category(ch)
    return cat[0] in ("L", "N") or cat in ("Mn", "Mc")


def clean(text, limit: int, multiline: bool = False) -> str:
    """Return `text` reduced to the allow-list and cut to `limit` characters."""
    if text is None:
        return ""
    s = str(text)[: max(1, limit) * _RAW_CAP_FACTOR]
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
    out, marks = [], 0
    for ch in s:
        if ch == "\n":
            out.append("\n" if multiline else " ")
            marks = 0
            continue
        cat = unicodedata.category(ch)
        if cat in ("Mn", "Mc"):
            # an accent must follow a letter, and a letter carries at most two
            prev = out[-1] if out else ""
            if marks >= 2 or not prev or unicodedata.category(prev)[0] not in ("L", "M"):
                continue
            marks += 1
            out.append(ch)
            continue
        marks = 0
        if _keep(ch):
            out.append(ch)
        elif cat.startswith("Z"):
            out.append(" ")          # any other kind of space becomes a plain space
        # everything else is dropped
    s = "".join(out)
    s = re.sub(r"[ ]{2,}", " ", s)
    if multiline:
        s = "\n".join(line.strip() for line in s.split("\n"))
        s = re.sub(r"\n{3,}", "\n\n", s)
    s = s.strip()
    if len(s) > limit:
        s = s[:limit].rstrip()
    return s


def clean_title(text) -> str:
    return clean(text, TITLE_MAX)


def clean_detail(text) -> str:
    return clean(text, DETAIL_MAX, multiline=True)


def clean_name(text) -> str:
    return clean(text, NAME_MAX)


_MD_SPECIAL = re.compile(r"([*_#+=\-!()])")


def md_inline(text, limit: int = TITLE_MAX) -> str:
    """Cleaned, single-line, and with the markdown characters that survive the allow-list
    backslash-escaped - for text placed in a rendered markdown line such as a heading."""
    return _MD_SPECIAL.sub(r"\\\1", clean(text, limit))
