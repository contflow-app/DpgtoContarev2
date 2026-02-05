from __future__ import annotations
from typing import Optional

FAIXAS = [
    (0, 2500, "Assistente I"),
    (2500, 3200, "Assistente II"),
    (3200, 4000, "Assistente III"),
    (4000, 5200, "Analista Júnior"),
    (5200, 7000, "Analista Pleno"),
    (7000, 999999, "Analista Sênior"),
]

FAMILIAS = {
    "DP": ["DP", "DEPARTAMENTO PESSOAL", "PESSOAL"],
    "FISCAL": ["FISCAL", "TRIBUT", "IMPOST", "ICMS", "ISS"],
    "CONTABIL": ["CONTABIL", "CONTÁBIL", "CONTABILIDADE", "BALANCO", "BALANÇO"],
    "FINANCEIRO": ["FINANCEIRO", "TESOURARIA", "CONTAS A PAGAR", "CONTAS A RECEBER"],
    "ADM": ["ADMIN", "ADMINISTRAT", "RECEPCAO", "RECEPÇÃO"],
}

def infer_familia(texto: str) -> str:
    t = (texto or "").upper()
    for fam, keys in FAMILIAS.items():
        if any(k in t for k in keys):
            return fam
    return "GERAL"

def nivel_por_salario(bruto: Optional[float]) -> Optional[str]:
    if bruto is None:
        return None
    for lo, hi, label in FAIXAS:
        if lo <= bruto < hi:
            return label
    return None

def cargo_final(familia: str, nivel: Optional[str]) -> Optional[str]:
    if not nivel:
        return None
    fam = familia or "GERAL"
    return nivel if fam == "GERAL" else f"{nivel} {fam}"
