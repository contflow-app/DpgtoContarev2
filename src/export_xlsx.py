from openpyxl import Workbook
def export_xlsx(df, path, logo=None):
    wb=Workbook()
    ws=wb.active
    ws.append(list(df.columns))
    for r in df.itertuples(index=False): ws.append(list(r))
    wb.save(path)