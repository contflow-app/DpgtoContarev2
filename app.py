from __future__ import annotations
import os, io, zipfile, tempfile
from pathlib import Path
import pandas as pd
import streamlit as st
import pdfplumber

from src.parsing_recibo import parse_recibo_pagamento_pdf
from src.matching import load_salario_real_xlsx, find_colaborador_ref
from src.cargos import infer_familia, nivel_por_salario, cargo_final
from src.export_xlsx import export_xlsx
from src.receipts_pdf import generate_all_receipts

APP_TITLE = "Demonstrativo de Pagamento Contare"
ROOT = Path(__file__).parent
LOGO_PATH = ROOT / "assets" / "logo.png"

st.set_page_config(page_title=APP_TITLE, layout="wide")

def compute_valor(bruto_planilha, ref_dias, salario_holerite, liquido_holerite):
    bruto_prop = bruto_planilha * (ref_dias / 30)
    if liquido_holerite > 0:
        return bruto_prop - salario_holerite + liquido_holerite, "PADRÃO"
    return bruto_prop - salario_holerite, "ESPECIAL (líquido=0)"

st.title(APP_TITLE)

pdf = st.file_uploader("Holerite (PDF)", type=["pdf"])
xlsx = st.file_uploader("Planilha salários (XLSX)", type=["xlsx"])

if not pdf or not xlsx:
    st.stop()

tmp = ROOT / ".tmp"
tmp.mkdir(exist_ok=True)
pdf_path = tmp / "holerite.pdf"
xlsx_path = tmp / "salarios.xlsx"
pdf_path.write_bytes(pdf.getbuffer())
xlsx_path.write_bytes(xlsx.getbuffer())

if st.button("Processar"):
    df_sal = load_salario_real_xlsx(str(xlsx_path))
    colabs, comp = parse_recibo_pagamento_pdf(str(pdf_path))

    rows = []
    for c in colabs:
        ref = find_colaborador_ref(df_sal, c["nome"])
        bruto = ref["bruto_referencial"]
        eventos = c["eventos"]

        salario = sum(e["provento"] or 0 for e in eventos if e["codigo"] in ("8781","8786"))
        ref_dias = next((float(e["referencia"]) for e in eventos if e["codigo"] in ("8781","8786") and e["referencia"]),30)
        liquido = c["liquido"] or 0

        valor, regra = compute_valor(bruto, ref_dias, salario, liquido)

        familia = infer_familia(ref.get("departamento",""))
        nivel = nivel_por_salario(bruto)
        cargo = cargo_final(familia, nivel)

        rows.append({
            "competencia": c["competencia"] or comp,
            "nome": c["nome"],
            "cargo": cargo,
            "bruto_planilha": bruto,
            "salario_holerite": salario,
            "liquido_holerite": liquido,
            "valor_a_pagar": valor,
            "regra": regra
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch")

    tmp_x = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    export_xlsx(df, tmp_x.name, str(LOGO_PATH) if LOGO_PATH.exists() else None)
    st.download_button("Baixar Excel", Path(tmp_x.name).read_bytes(), "consolidado.xlsx")