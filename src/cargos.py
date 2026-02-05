def infer_familia(txt): return "GERAL"
def nivel_por_salario(b):
    if b < 3000: return "Assistente"
    if b < 5000: return "Analista Jr"
    return "Analista Pleno"
def cargo_final(f,n): return n