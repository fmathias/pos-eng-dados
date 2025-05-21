import os
import ast

import pandas as pd
pd.set_option('display.max_colwidth', None)
import psycopg2
import requests
import time
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Carregar variáveis de ambiente
load_dotenv()

from utils.connect_vault import *
from utils.connect_postgres import *
from utils.execute_pg_query import *
from utils.extract import *
from utils.view import *


#   Exercício 1 – Temperatura Média das Capitais dos Clientes
# 	•	Recupere as cidades dos clientes com mais de 10 transações.
# 	•	Use a WeatherAPI para buscar a temperatura atual dessas cidades.
# 	•	Calcule a temperatura média ponderada por número de clientes.
# 	•	Insight esperado: quais cidades concentram clientes e temperaturas extremas?

def exercicio1():
    query_ex1 = """
                WITH CTE AS (
                    SELECT city.city, COUNT(*) AS qtd_transacoes
                    FROM rental
                    INNER JOIN customer ON rental.customer_id = customer.customer_id
                    INNER JOIN address ON customer.address_id = address.address_id
                    INNER JOIN city ON address.city_id = city.city_id
                    GROUP BY city.city
                    HAVING COUNT(*) > 10
                    ORDER BY city.city
                )
                SELECT city, qtd_transacoes FROM CTE
                LIMIT 10;

                """
    result_query = run_query(query_ex1)

    temperaturas = []
    for _, row in result_query.iterrows():
        cidade = row["city"]
        peso = row["qtd_transacoes"]

        clima = extract_dados_clima(cidade)

        if clima and "current" in clima:
            temperatura_cidade = clima["current"]["temp_c"]
            temperaturas.append({
                "cidade": cidade,
                "qtd_transacoes": peso,
                "temperatura": temperatura_cidade
            })

    df_temperaturas = pd.DataFrame(temperaturas)

    ## Cálculo da média é feito pela fórmula: (temperatura x qtd_transações / qtd_transações)    
    media_ponderada = (df_temperaturas["temperatura"] * df_temperaturas["qtd_transacoes"]).sum() / df_temperaturas["qtd_transacoes"].sum()
    
    return media_ponderada

#-----------------------------/////--------------------------------------

#   Exercício 2 – Receita Bruta em Cidades com Clima Ameno
# 	•	Calcule a receita bruta por cidade.
# 	•	Use a WeatherAPI para consultar a temperatura atual.
# 	•	Filtre apenas cidades com temperatura entre 18°C e 24°C.
# 	•	Resultado: qual o faturamento total vindo dessas cidades?

def exercicio2():
    
    query_ex2 = """
            SELECT city.city, SUM(payment.amount) AS receita_total
            FROM payment
            JOIN customer ON payment.customer_id = customer.customer_id
            JOIN address ON customer.address_id = address.address_id
            JOIN city ON address.city_id = city.city_id
            GROUP BY city.city
            ORDER BY receita_total DESC limit 10
            """
    result_query = run_query(query_ex2)

    result_query["temperatura"] = result_query["city"].apply(
                        lambda cidade: extract_dados_clima(cidade).get("current", {}).get("temp_c")
        if extract_dados_clima(cidade) else None
    )

    result_query = result_query.dropna(subset=["temperatura"])

    df_ameno = result_query[(result_query["temperatura"] >= 18) & (result_query["temperatura"] <= 24)]

    total_receita_cidades_temp_ameno = df_ameno["receita_total"].sum()

    #print(df_ameno,total_receita_cidades_temp_ameno)

    return df_ameno, total_receita_cidades_temp_ameno


#-----------------------------/////--------------------------------------


#   Exercício 3 – Aluguel de Filmes por Região e População
# 	•	Identifique os países dos clientes com maior número de aluguéis.
# 	•	Use a REST Countries API para obter a população desses países.
# 	•	Calcule o número de aluguéis por 1.000 habitantes.
# 	•	Análise: quais países são mais “cinéfilos” proporcionalmente?

def exercicio3():
    
    query_ex3 = """

                SELECT 
                    country.country AS pais,          
                    COUNT(DISTINCT rental.rental_id) AS num_alugueis    
                FROM rental
                    JOIN inventory ON rental.inventory_id = inventory.inventory_id   
                    JOIN film ON inventory.film_id = film.film_id        
                    JOIN customer ON rental.customer_id = customer.customer_id   
                    JOIN address ON customer.address_id = address.address_id    
                    JOIN city ON address.city_id = city.city_id   
                    JOIN country ON city.country_id = country.country_id 
                GROUP BY country.country   
                ORDER BY num_alugueis DESC    
                LIMIT 10
            
        """
    
    result_query = run_query(query_ex3)

    result_query["populacao"] = result_query["pais"].apply(
        lambda pais: extract_dados_pais_por_nome(pais)[0]["population"]
            if extract_dados_pais_por_nome(pais) else None
        )
    
    result_query["vl_aluguel_1k_habitantes"] = ( 
        (result_query["num_alugueis"] / result_query["populacao"]) * 1000
        ).round(4)

    df_final = result_query.sort_values("vl_aluguel_1k_habitantes", ascending=False)

    return df_final


#-----------------------------/////--------------------------------------

#   Exercício 4 – Filmes Mais Populares em Cidades Poluídas
# 	•	Liste as 10 cidades com maior número de clientes.
# 	•	Use a AirVisual API para consultar o AQI dessas cidades.
# 	•	Relacione os filmes mais alugados em cidades com AQI > 150.
# 	•	Discussão: poluição impacta preferências de filmes?



def exercicio4_1():
    query_ex4_1 = """
        WITH CTE as (
            SELECT 
                city.city as cidade, 
                address.district as estado,
                country.country as pais,
                count(customer.customer_id) as qtd_clientes
            FROM customer
            INNER JOIN address ON customer.address_id = address.address_id 
            INNER JOIN city    ON address.city_id     = city.city_id 
            INNER JOIN country ON city.country_id     = country.country_id 
            --WHERE city.city LIKE 'Abu Dhabi'
            GROUP BY city.city_id, address.district, country.country 
            ORDER BY qtd_clientes DESC
            LIMIT 50
        )
        SELECT cidade, estado, pais FROM CTE;
    """
 
    result_query_cidades = run_query(query_ex4_1)
    print(result_query_cidades)

    try:
        result_query_cidades["api_resposta"] = result_query_cidades.apply(
            lambda funcao: extract_dados_qualidade_ar_cidade(
                funcao['cidade'], funcao['estado'], funcao['pais']
            ),
            axis=1
        )

        result_query_cidades["aqius"] = result_query_cidades["api_resposta"].apply(
            lambda aqi: aqi["data"]["current"]["pollution"]["aqius"]
            if isinstance(aqi, dict) and "data" in aqi else None
        )

        return result_query_cidades[["cidade", "estado", "pais", "aqius"]]    

    except Exception as e:
        print(f"Erro ao processar AQI: {e}")
        return None

        


def exercicio4_2():
        query_ex4_2 = """
        SELECT 
        city.city as cidade,
        film.film_id,
        film.title,
        COUNT(rental.rental_id) AS total_alugueis
        FROM rental
        INNER JOIN inventory ON rental.inventory_id = inventory.inventory_id
        INNER JOIN film ON inventory.film_id = film.film_id
        INNER JOIN customer ON rental.customer_id = customer.customer_id
        INNER JOIN address ON customer.address_id = address.address_id
        INNER JOIN city ON address.city_id = city.city_id
        GROUP BY city.city, film.film_id, film.title
        ORDER BY city.city, total_alugueis DESC;

        """
        result_query_filmes = run_query(query_ex4_2)

        return result_query_filmes
        

df_aqi_cidades = exercicio4_1()
df_filmes_cidades = exercicio4_2()


df_mergeado = pd.merge(df_aqi_cidades, df_filmes_cidades, on="cidade", how="inner")

print(df_mergeado)


#-----------------------------/////--------------------------------------


#   Exercício 5 – Clientes em Áreas Críticas
# 	•	Recupere os clientes com endereço em cidades com AQI acima de 130.
# 	•	Combine nome do cliente, cidade, país, temperatura e AQI.
# 	•	Classifique os clientes em “zona de atenção” com base nos critérios ambientais.

# ⸻




#-----------------------------/////--------------------------------------

#   Exercício 6 – Receita por Continente
# 	•	Use a REST Countries API para mapear o continente de cada país.
# 	•	Agrupe a receita total por continente.
# 	•	Exiba os resultados em um gráfico de pizza com matplotlib.


def exercicio_6_1():
    
        query_ex6 = """
                SELECT 
                COUNTRY.country as pais, 
                SUM(payment.amount) as receita_total
                FROM payment
                JOIN customer ON payment.customer_id = customer.customer_id
                JOIN address ON customer.address_id = address.address_id
                JOIN city ON address.city_id = city.city_id
                JOIN country  ON country.country_id = city.country_id
                GROUP BY country.country
                ORDER BY receita_total DESC
                """

        result_query_receita = run_query(query_ex6)
        #print(result_query_recita)

        result_query_receita["continente"] = result_query_receita["pais"].apply(
        lambda pais: extract_dados_pais_por_nome(pais)[0]["continents"][0]
                if extract_dados_pais_por_nome(pais) else None
        )

        result_query_receita.to_csv("python/entrega1/data/pais_continente.csv", index=False)


        return None        

def exercicio_6_2():

        result_query_receita = pd.read_csv("python/entrega1/data/pais_continente.csv", sep=",", encoding="utf-8")

        df_receita_continente = result_query_receita\
                                .groupby(['continente'])\
                                        .agg(receita_total=('receita_total', 'sum')).reset_index()

        plot_pizza(df_receita_continente, 'receita_total', 'continente', 'Receita total por continente' )

receita_continente = exercicio_6_1()
exercicio_6_2() #monta o gráfico de pizza



#-----------------------------/////--------------------------------------

#   Exercício 7 – Tempo Médio de Aluguel vs Clima
# 	•	Calcule o tempo médio de aluguel por cidade (entre rental_date e return_date).
# 	•	Combine com a temperatura atual dessas cidades.
# 	•	Visualize a correlação entre temperatura e tempo médio de aluguel (scatterplot + linha de tendência).



































