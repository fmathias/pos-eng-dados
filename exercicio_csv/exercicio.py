import pandas as pd
from datetime import time
import matplotlib.pyplot as plt


df_csv = pd.read_csv("C:\\Users\\FernandaMathias\\OneDrive - EloGroup\Documentos\\REPOS\\000 - ESTUDOS\\REPOS\\PUC\\python\\exercicio_csv\\Clima__50_mil_linhas.csv")
df_csv['date'] = pd.to_datetime(df_csv['time']).dt.date

"""
Filtre o DataFrame para mostrar apenas os registros da cidade de “Manaus”
"""

# filtro_manaus = df_csv[df_csv['cidade'] == "Manaus"]
# print(filtro_manaus)

"""
Média de temperatura por cidade
Calcule a temperatura média (temp_c) por cidade, ordenando da maior para a
menor.
"""

# temp_cidade = df_csv.groupby('cidade')['temp_c'].mean().reset_index()
# print(temp_cidade)

"""
Encontre os 5 dias com maior precipitação total. Use a coluna precip_mm
somando por data (time.date()).
"""

# precip_cidade = df_csv.groupby('date')['precip_mm'].sum().reset_index()
# precip_cidade = precip_cidade.sort_values('precip_mm', ascending=0).head(5)
# print(precip_cidade)

"""
Distribuição do UV por período do dia
Crie uma análise da média de uv agrupada pela coluna is_day (0 = noite, 1 = dia)
"""

# uv = df_csv.groupby('is_day')['uv'].mean().reset_index()
# print(uv)

"""
Conte quantas vezes cada condição climática (condicao) apareceu no dataset.
"""
# cond_cimatica = df_csv.groupby('condicao').size().reset_index(name='count')
# print(cond_cimatica)

"""
Quantos registros possuem feelslike_c acima de 35°C? Qual a média de umidade
nesses casos?
"""
# feelslike_35 = df_csv[df_csv['feelslike_c']>=35]
# feelslike_35 = feelslike_35.groupby('feelslike_c').size().reset_index(name='count')
# print(feelslike_35)

"""
Crie uma nova coluna chamada delta_sensacao com a diferença entre feelslike_c e
temp_c
"""

# df_csv['delta_sensacao'] = df_csv['feelslike_c'] - df_csv['temp_c']
# print(df_csv)

"""
Qual região apresentou a maior média de wind_kph?
"""
# regiao_wind_kph = df_csv.groupby('regiao')['wind_kph'].sum().reset_index()
# print(regiao_wind_kph)


"""
Crie uma coluna chamada visibilidade_classificada com:
○ “Alta” para vis_km >= 10
○ “Média” para vis_km >= 5 e < 10
○ “Baixa” para vis_km < 5
"""

# def classificar_visibilidade(valor):
#     if valor >= 10:
#         return 'Alta'
#     elif valor >= 5:
#         return 'Média'
#     else:
#         return 'Baixa'

# df_csv['visibilidade_classificada'] = df_csv['vis_km'].apply(classificar_visibilidade)

# print(df_csv)


"""
Usando Matplotlib, crie um gráfico de linha com a variação de temperatura (temp_c)
ao longo do tempo para a cidade de Belo Horizonte
"""

df_bh = df_csv[df_csv["cidade"] == "Belo Horizonte"]
plt.figure(figsize=(12, 4))
plt.plot(df_bh["time"], df_bh["temp_c"], linewidth=0.5)
plt.title("Variação da Temperatura em Belo Horizonte")
plt.xlabel("Tempo")
plt.ylabel("Temperatura (°C)")
plt.tight_layout()
plt.grid(True)
plt.show()