import re

ISIN_RE = re.compile(r"\b[A-Z]{2}[A-Z0-9]{10}\b")
WKN_RE  = re.compile(r"\b[A-Z0-9]{6}\b")

def de_number_to_float(s: str | None) -> float:
    if s is None:
        return 0.0
    s = s.replace("\xa0", " ").strip()
    s = re.sub(r"[^\d,.\-]", "", s)
    if not s:
        return 0.0
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0

def parse_qty(text: str) -> float:
    return de_number_to_float(text)

def parse_eur(text: str) -> float:
    return de_number_to_float(text)

def extract_isin_wkn(cell_text: str) -> tuple[str | None, str | None]:
    t = cell_text.replace("\xa0", " ").strip()
    isin = (ISIN_RE.search(t).group(0) if ISIN_RE.search(t) else None)
    wkn = None
    if "|" in t:
        right = t.split("|", 1)[1]
        m = WKN_RE.search(right)
        if m:
            wkn = m.group(0)
    else:
        m = WKN_RE.search(t)
        if m:
            wkn = m.group(0)
    return isin, wkn
