import pdfplumber, re
from src.utils import parse_money_any

def parse_recibo_pagamento_pdf(path):
    out=[]
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            t=p.extract_text() or ""
            nome=re.search(r"Nome\s*:\s*(.*)",t)
            liq=re.search(r"L[ií]quido\s*(\d+[.,]\d+)",t)
            eventos=[]
            for l in t.splitlines():
                m=re.match(r"(8781|8786)\s+.*?(\d+[.,]\d+)\s+(\d+[.,]\d+)",l)
                if m:
                    eventos.append({"codigo":m.group(1),"referencia":m.group(2),"provento":parse_money_any(m.group(3))})
            out.append({
                "nome": nome.group(1).strip() if nome else "",
                "liquido": parse_money_any(liq.group(1)) if liq else 0,
                "eventos": eventos,
                "competencia": None
            })
    return out, None