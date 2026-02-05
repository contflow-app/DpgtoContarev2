from __future__ import annotations
from typing import Optional
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.drawing.image import Image as XLImage

def export_xlsx(df: pd.DataFrame, out_path: str, logo_path: Optional[str] = None) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Consolidado"
    if logo_path:
        try:
            img = XLImage(logo_path)
            img.height = 60
            img.width = 120
            ws.add_image(img, "A1")
        except Exception:
            pass
    for row in dataframe_to_rows(df, index=False, header=True):
        ws.append(row)
    wb.save(out_path)
