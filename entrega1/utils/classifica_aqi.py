import pandas as pd

def classificar_aqi(valor):
    if pd.isna(valor):
        return "Desconhecido"
    elif valor <= 50:
        return "Bom (Verde)"
    elif valor <= 100:
        return "Moderado (Amarelo)"
    elif valor <= 150:
        return "Ruim para Grupos Sensíveis (Laranja)"
    elif valor <= 200:
        return "Ruim (Vermelho)"
    elif valor <= 300:
        return "Muito Ruim (Roxo)"
    elif valor <= 500:
        return "Perigoso (Marrom)"
    else:
        return "Fora da escala"