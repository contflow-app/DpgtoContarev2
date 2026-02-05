from __future__ import annotations
from typing import Dict, List, Optional
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

def _money(v) -> str:
    if v is None:
        return "-"
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "-"

def generate_receipt_pdf(row: Dict, out_path: str, empresa_nome: str, logo_path: Optional[str] = None) -> None:
    c = canvas.Canvas(out_path, pagesize=A4)
    W, H = A4

    if logo_path and Path(logo_path).exists():
        try:
            c.drawImage(str(logo_path), 18*mm, H-30*mm, width=35*mm, height=18*mm, mask='auto')
        except Exception:
            pass

    c.setFont("Helvetica-Bold", 12)
    c.drawString(60*mm, H-20*mm, "DEMONSTRATIVO DE PAGAMENTO (COMPLEMENTAR)")
    c.setFont("Helvetica", 10)
    c.drawString(60*mm, H-26*mm, f"Empresa: {empresa_nome}")
    c.drawRightString(W-18*mm, H-26*mm, f"Competência: {row.get('competencia') or '-'}")

    y = H-42*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(18*mm, y, f"Colaborador: {row.get('nome') or '-'}")
    y -= 6*mm
    c.setFont("Helvetica", 9)
    c.drawString(18*mm, y, f"Cargo: {row.get('cargo_plano') or row.get('cargo') or '-'}")
    y -= 10*mm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(18*mm, y, "Cálculo (regra simplificada)")
    y -= 7*mm
    c.setFont("Helvetica", 9)

    c.drawString(18*mm, y, "Salário Bruto (planilha proporcional)")
    c.drawRightString(W-18*mm, y, _money(row.get("bruto_planilha_proporcional")))
    y -= 6*mm

    c.drawString(18*mm, y, "(-) Salário contratual (holerite 8781/8786)")
    c.drawRightString(W-18*mm, y, _money(row.get("salario_holerite")))
    y -= 6*mm

    c.drawString(18*mm, y, "(+) Líquido holerite oficial")
    c.drawRightString(W-18*mm, y, _money(row.get("liquido_holerite")))
    y -= 8*mm

    c.setFont("Helvetica-Bold", 11)
    c.line(18*mm, y, W-18*mm, y)
    y -= 10*mm
    c.drawString(18*mm, y, "VALOR LÍQUIDO A PAGAR")
    c.drawRightString(W-18*mm, y, _money(row.get("valor_a_pagar")))

    y -= 12*mm
    c.setFont("Helvetica", 8)
    c.drawString(18*mm, y, f"Regra aplicada: {row.get('regra') or '-'}")
    c.drawString(18*mm, 15*mm, "Gerado automaticamente — Demonstrativo de Pagamento Contare")

    c.showPage()
    c.save()

def generate_all_receipts(rows: List[Dict], out_dir: str, empresa_nome: str = "Contare", logo_path: Optional[str] = None) -> List[str]:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    outs: List[str] = []
    for r in rows:
        nome = (r.get("nome") or "COLAB").replace("/", "-")
        comp = (r.get("competencia") or "COMP").replace("/", "-")
        out_path = str(Path(out_dir) / f"demonstrativo_{comp}__{nome}.pdf")
        generate_receipt_pdf(r, out_path, empresa_nome=empresa_nome, logo_path=logo_path)
        outs.append(out_path)
    return outs
