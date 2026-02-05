from __future__ import annotations
import io, zipfile, tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from src.parsing_recibo import parse_recibo_pagamento_pdf
from src.matching import load_salario_real_xlsx, find_colaborador_ref
from src.cargos import infer_familia, nivel_por_salario, cargo_final
from src.export_xlsx import export_xlsx
from src.receipts_pdf import generate_all_receipts

APP_TITLE = "Demonstrativo de Pagamento Contare"
ROOT = Path(__file__).parent
LOGO_PATH = ROOT / "assets" / "logo.png"

st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)

with st.sidebar:
    st.header("Configurações")
    empresa_nome = st.text_input("Empresa", value="Contare")
    limiar_zero = st.number_input("Limiar líquido ~0", value=0.0, min_value=0.0)

pdf = st.file_uploader("Holerite (PDF)", type=["pdf"])
xlsx = st.file_uploader("Planilha salários (XLSX) — colunas: Nome e Bruto", type=["xlsx"])

if not pdf or not xlsx:
    st.info("Envie o PDF e a planilha para continuar.")
    st.stop()

tmp_dir = ROOT / ".tmp"
tmp_dir.mkdir(exist_ok=True)
pdf_path = tmp_dir / "holerite.pdf"
xlsx_path = tmp_dir / "salarios.xlsx"
pdf_path.write_bytes(pdf.getbuffer())
xlsx_path.write_bytes(xlsx.getbuffer())

def compute_valor(bruto_planilha: float, ref_dias: float, salario_holerite: float, liquido_holerite: float) -> tuple[float, str, float]:
    bruto_prop = bruto_planilha * (ref_dias / 30.0)
    if liquido_holerite > 0:
        return (bruto_prop - salario_holerite + liquido_holerite), "PADRÃO", bruto_prop
    return (bruto_prop - salario_holerite), "ESPECIAL (líquido=0)", bruto_prop

if st.button("Processar", type="primary"):
    df_sal = load_salario_real_xlsx(str(xlsx_path))
    colabs, comp_global = parse_recibo_pagamento_pdf(str(pdf_path))

    rows = []
    for c in colabs:
        nome_pdf = (c.get("nome") or "").strip()
        ref = find_colaborador_ref(df_sal, nome_pdf)
        bruto = ref.get("bruto_referencial")
        if bruto is None:
            continue
        bruto = float(bruto)

        eventos = c.get("eventos") or []
        salario = 0.0
        ref_dias = 30.0
        for e in eventos:
            if str(e.get("codigo")) in ("8781","8786"):
                salario += float(e.get("provento") or 0.0)
                r = e.get("referencia")
                try:
                    if r is not None and str(r).strip():
                        ref_dias = float(str(r).replace(".", "").replace(",", "."))
                except Exception:
                    pass

        liquido = float(c.get("liquido") or 0.0)
        if liquido <= limiar_zero:
            liquido = 0.0

        valor, regra, bruto_prop = compute_valor(bruto, ref_dias, salario, liquido)
        if valor < 0:
            valor = 0.0

        depto = ref.get("departamento","")
        cargo_base = ref.get("cargo","")
        familia = infer_familia(f"{depto} {cargo_base}")
        nivel = nivel_por_salario(bruto)
        cargo_plano = cargo_final(familia, nivel) or cargo_base or ""

        rows.append({
            "competencia": c.get("competencia") or comp_global,
            "nome": nome_pdf or ref.get("nome") or "",
            "departamento": depto,
            "cargo_plano": cargo_plano,
            "bruto_planilha": bruto,
            "ref_dias": ref_dias,
            "bruto_planilha_proporcional": bruto_prop,
            "salario_holerite": salario,
            "liquido_holerite": liquido,
            "valor_a_pagar": valor,
            "regra": regra,
        })

    df = pd.DataFrame(rows)
    st.session_state["df"] = df

df = st.session_state.get("df")
if df is None:
    st.stop()

st.subheader("Consolidado")
st.dataframe(df, width="stretch")

st.subheader("Exportações")
colA, colB = st.columns(2)

with colA:
    tmp_x = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    tmp_x.close()
    export_xlsx(df, tmp_x.name, str(LOGO_PATH) if LOGO_PATH.exists() else None)
    st.download_button("Baixar Excel", Path(tmp_x.name).read_bytes(), "consolidado.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    Path(tmp_x.name).unlink(missing_ok=True)

with colB:
    tmpdir = tempfile.TemporaryDirectory()
    pdf_paths = generate_all_receipts(df.to_dict("records"), out_dir=tmpdir.name, empresa_nome=empresa_nome,
                                      logo_path=str(LOGO_PATH) if LOGO_PATH.exists() else None)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in pdf_paths:
            z.write(p, arcname=Path(p).name)
    buf.seek(0)
    st.download_button("Baixar Recibos (PDF em ZIP)", buf.getvalue(), "recibos_pdf.zip", mime="application/zip")
