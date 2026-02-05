from __future__ import annotations
import re
from typing import Optional

MONEY_RE = re.compile(r"-?\d{1,3}(?:\.\d{3})*,\d{2}|-?\d+\.\d{2}")

def normalize_name(s: str) -> str:
    s = (s or "").strip().upper()
    s = re.sub(r"\s+", " ", s)
    trans = str.maketrans(
        "ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ",
        "AAAAAEEEEIIIIOOOOOUUUUCN",
    )
    return s.translate(trans)

def parse_money_any(v) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        try:
            return float(v)
        except Exception:
            return None
    s = str(v).strip()
    if not s:
        return None
    s = re.sub(r"[^0-9,\.\-]", "", s)
    if not s:
        return None
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None
