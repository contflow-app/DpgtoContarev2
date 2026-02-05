from __future__ import annotations
from typing import Dict
import pandas as pd
import re
from .utils import normalize_name, parse_money_any

def _pick_col(df: pd.DataFrame, candidates):
    cols = list(df.columns)
    cols_norm = {c: normalize_name(str(c)) for c in cols}
    for cand in candidates:
        cn = normalize_name(cand)
        for c, n in cols_norm.items():
            if cn == n:
                return c
    for cand in candidates:
        cn = normalize_name(cand)
        for c, n in cols_norm.items():
            if cn in n:
                return c
    return None

def load_salario_real_xlsx(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    name_col = _pick_col(df, ["NOME", "COLABORADOR", "FUNCIONARIO", "FUNCIONÁRIO"])
    bruto_col = _pick_col(df, ["BRUTO", "SALARIO", "SALÁRIO", "VALOR", "REMUNERACAO", "REMUNERAÇÃO"])
    if name_col is None or bruto_col is None:
        raise ValueError("Planilha deve ter 2 colunas: Nome e Bruto (salário referencial).")
    out = pd.DataFrame({
        "nome": df[name_col].astype(str).fillna(""),
        "nome_norm": df[name_col].astype(str).fillna("").map(normalize_name),
        "bruto_referencial": df[bruto_col].map(parse_money_any),
        "departamento": df[_pick_col(df, ["DEPARTAMENTO","DEPTO","SETOR","AREA","ÁREA"])].astype(str).fillna("") if _pick_col(df, ["DEPARTAMENTO","DEPTO","SETOR","AREA","ÁREA"]) else "",
        "cargo": df[_pick_col(df, ["CARGO","FUNCAO","FUNÇÃO"])].astype(str).fillna("") if _pick_col(df, ["CARGO","FUNCAO","FUNÇÃO"]) else "",
        "status": df[_pick_col(df, ["STATUS","SITUACAO","SITUAÇÃO"])].astype(str).fillna("") if _pick_col(df, ["STATUS","SITUACAO","SITUAÇÃO"]) else "",
    })
    out = out[out["bruto_referencial"].notna()]
    return out.reset_index(drop=True)

def find_colaborador_ref(df_sal: pd.DataFrame, nome_pdf: str) -> Dict:
    n = normalize_name(nome_pdf)
    if not n:
        return {}
    hit = df_sal[df_sal["nome_norm"] == n]
    if len(hit) >= 1:
        return hit.iloc[0].to_dict()
    # contains fallback
    hit = df_sal[df_sal["nome_norm"].str.contains(re.escape(n), na=False)]
    if len(hit) >= 1:
        return hit.iloc[0].to_dict()
    # token overlap fallback
    def score(a,b): return len(set(a.split()) & set(b.split()))
    best = None; best_s = -1
    for _, r in df_sal.iterrows():
        s = score(n, r["nome_norm"])
        if s > best_s:
            best_s = s; best = r
    return best.to_dict() if best is not None else {}
