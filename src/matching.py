import pandas as pd
from src.utils import parse_money_any

def load_salario_real_xlsx(path):
    df = pd.read_excel(path)
    return pd.DataFrame({
        "nome": df.iloc[:,0].astype(str),
        "bruto_referencial": df.iloc[:,1].map(parse_money_any)
    })

def find_colaborador_ref(df, nome):
    r = df[df["nome"].str.upper()==nome.upper()]
    return r.iloc[0].to_dict() if len(r) else {}