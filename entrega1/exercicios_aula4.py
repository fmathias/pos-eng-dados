import os

#import matplotlib.pyplot as plt
import pandas as pd
pd.set_option('display.max_colwidth', None)
import psycopg2
import requests
#import seaborn as sns
import time
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Carregar variáveis de ambiente
load_dotenv()

from utils.connect_vault import *
from utils.connect_postgres import *
from utils.execute_pg_query import *
from utils.extract import *


#   Exercício 1 – Temperatura Média das Capitais dos Clientes
# 	•	Recupere as cidades dos clientes com mais de 10 transações.
# 	•	Use a WeatherAPI para buscar a temperatura atual dessas cidades.
# 	•	Calcule a temperatura média ponderada por número de clientes.
# 	•	Insight esperado: quais cidades concentram clientes e temperaturas extremas?

# def exercicio1():
#     query_ex1 = """
#                 WITH CTE AS (
#                     SELECT city.city, COUNT(*) AS qtd_transacoes
#                     FROM rental
#                     INNER JOIN customer ON rental.customer_id = customer.customer_id
#                     INNER JOIN address ON customer.address_id = address.address_id
#                     INNER JOIN city ON address.city_id = city.city_id
#                     GROUP BY city.city
#                     HAVING COUNT(*) > 10
#                     ORDER BY city.city
#                 )
#                 SELECT city, qtd_transacoes FROM CTE
#                 LIMIT 10;

#                 """
#     result_query = run_query(query_ex1)

#     temperaturas = []
#     for _, row in result_query.iterrows():
#         cidade = row["city"]
#         peso = row["qtd_transacoes"]

#         clima = extract_dados_clima(cidade)

#         if clima and "current" in clima:
#             temperatura_cidade = clima["current"]["temp_c"]
#             temperaturas.append({
#                 "cidade": cidade,
#                 "qtd_transacoes": peso,
#                 "temperatura": temperatura_cidade
#             })

#     df_temperaturas = pd.DataFrame(temperaturas)

#     ## Cálculo da média é feito pela fórmula: (temperatura x qtd_transações / qtd_transações)    
#     media_ponderada = (df_temperaturas["temperatura"] * df_temperaturas["qtd_transacoes"]).sum() / df_temperaturas["qtd_transacoes"].sum()
    
#     return media_ponderada

#-----------------------------/////--------------------------------------

#   Exercício 2 – Receita Bruta em Cidades com Clima Ameno
# 	•	Calcule a receita bruta por cidade.
# 	•	Use a WeatherAPI para consultar a temperatura atual.
# 	•	Filtre apenas cidades com temperatura entre 18°C e 24°C.
# 	•	Resultado: qual o faturamento total vindo dessas cidades?

# def exercicio2():
    
#     query_ex2 = """
#             SELECT city.city, SUM(payment.amount) AS receita_total
#             FROM payment
#             JOIN customer ON payment.customer_id = customer.customer_id
#             JOIN address ON customer.address_id = address.address_id
#             JOIN city ON address.city_id = city.city_id
#             GROUP BY city.city
#             ORDER BY receita_total DESC limit 10
#             """
#     result_query = run_query(query_ex2)

#     result_query["temperatura"] = result_query["city"].apply(
#                         lambda cidade: extract_dados_clima(cidade).get("current", {}).get("temp_c")
#         if extract_dados_clima(cidade) else None
#     )

#     result_query = result_query.dropna(subset=["temperatura"])

#     df_ameno = result_query[(result_query["temperatura"] >= 18) & (result_query["temperatura"] <= 24)]

#     total_receita_cidades_temp_ameno = df_ameno["receita_total"].sum()

#     #print(df_ameno,total_receita_cidades_temp_ameno)

#     return df_ameno, total_receita_cidades_temp_ameno


#-----------------------------/////--------------------------------------


#   Exercício 3 – Aluguel de Filmes por Região e População
# 	•	Identifique os países dos clientes com maior número de aluguéis.
# 	•	Use a REST Countries API para obter a população desses países.
# 	•	Calcule o número de aluguéis por 1.000 habitantes.
# 	•	Análise: quais países são mais “cinéfilos” proporcionalmente?







































