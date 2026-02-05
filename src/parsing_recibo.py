from __future__ import annotations
import re
from typing import List, Dict, Tuple, Optional
import pdfplumber
from .utils import parse_money_any

SALARIO_CODES = ("8781","8786")

def parse_recibo_pagamento_pdf(path: str) -> Tuple[List[Dict], Optional[str]]:
    out: List[Dict] = []
    competencia_global = None

    with pdfplumber.open(path) as pdf:
        for page_index, p in enumerate(pdf.pages):
            t = p.extract_text() or ""

            m_nome = re.search(r"Nome\s*:\s*(.+)", t, flags=re.IGNORECASE)
            nome = (m_nome.group(1).strip() if m_nome else "").split("  ")[0].strip()

            m_comp = re.search(r"Compet[êe]ncia\s*(\d{2}/\d{4})", t, flags=re.IGNORECASE)
            comp = m_comp.group(1) if m_comp else None
            if comp and not competencia_global:
                competencia_global = comp

            m_liq = re.search(r"L[ií]quido\s+([0-9\.]+,[0-9]{2}|[0-9]+\.[0-9]{2})", t, flags=re.IGNORECASE)
            liquido = parse_money_any(m_liq.group(1)) if m_liq else 0.0

            eventos = []
            for line in t.splitlines():
                # tenta capturar: CODIGO ... REF ... VALOR
                mm = re.match(r"^(\d{4})\s+(.+?)\s+(\d{1,3}(?:\.\d{3})*,\d{2}|\d+\.\d{2})\s+(\d{1,3}(?:\.\d{3})*,\d{2}|\d+\.\d{2})\s*$", line.strip())
                if not mm:
                    continue
                codigo = mm.group(1)
                desc = mm.group(2).strip()
                ref = mm.group(3).strip()
                val = parse_money_any(mm.group(4))
                if codigo in SALARIO_CODES:
                    eventos.append({"codigo": codigo, "descricao": desc, "referencia": ref, "provento": val, "desconto": None})

            out.append({
                "page_index": page_index,
                "competencia": comp,
                "nome": nome,
                "liquido": liquido,
                "eventos": eventos,
            })

    return out, competencia_global
