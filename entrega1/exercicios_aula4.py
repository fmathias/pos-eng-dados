import os
import ast
import time
import numpy as np
import pandas as pd
pd.set_option('display.max_colwidth', None)
import psycopg2
import requests

import pycountry
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Carregar variáveis de ambiente
load_dotenv()

# from utils.connect_vault import *
# from utils.connect_postgres import *
from utils.execute_pg_query import *
from utils.extract import *
from utils.load import *
from utils.classifica_aqi import *
from utils.view import *

path_arquivo_trusted = "trusted/geonames/cidade_estado_pais"
file_name_trusted = "base_cidades_refinada"

#   Exercício 1 – Temperatura Média das Capitais dos Clientes
# 	•	Recupere as cidades dos clientes com mais de 10 transações.
# 	•	Use a WeatherAPI para buscar a temperatura atual dessas cidades.
# 	•	Calcule a temperatura média ponderada por número de clientes.
# 	•	Insight esperado: quais cidades concentram clientes e temperaturas extremas?

def exercicio1():        

        path_arquivo_final = "refined/exercicio1/"
        file_name_final = "media_ponderada"

        query_ex1 = """
                WITH CTE AS (
                        SELECT city.city as cidade, 
                        COUNT(*) AS qtd_transacoes
                        FROM rental
                        INNER JOIN customer ON rental.customer_id = customer.customer_id
                        INNER JOIN address ON customer.address_id = address.address_id
                        INNER JOIN city ON address.city_id = city.city_id
                        GROUP BY city.city
                        HAVING COUNT(*) > 10
                        ORDER BY qtd_transacoes
                )
                SELECT cidade, qtd_transacoes FROM CTE
                LIMIT 10;

                """
        result_query = run_query(query_ex1)

        base_cidades = pd.read_csv(f"{path_projeto}/{path_arquivo_trusted}/{file_name_trusted}.csv", sep=';')

        df_mergeado = pd.merge(result_query, base_cidades, on="cidade", how="inner")

        temperaturas = []

        for _, row in df_mergeado.iterrows():
                cidade = row["cidade"]

                try:
                        clima = extract_dados_clima(cidade)
                        time.sleep(1)  

                        if clima and "current" in clima:

                                temperaturas.append({
                                "cidade": cidade,
                                "qtd_transacoes": row["qtd_transacoes"],
                                "temperatura": clima["current"]["temp_c"],

                                })

                except Exception as e:
                        print(f"Erro ao buscar temperatura para {cidade}: {e}")
    
        df_temperaturas = pd.DataFrame(temperaturas)

        media_ponderada = (df_temperaturas["temperatura"] * df_temperaturas["qtd_transacoes"]).sum() / df_temperaturas["qtd_transacoes"].sum()

        df_resultado = pd.DataFrame([{"media_ponderada_temperatura": media_ponderada}])
        df_resultado.to_csv(f"{path_projeto}/{path_arquivo_final}/{file_name_final}.csv", index=False, sep=';')

    

#exercicio1()




#-----------------------------/////--------------------------------------

#   Exercício 2 – Receita Bruta em Cidades com Clima Ameno
# 	•	Calcule a receita bruta por cidade.
# 	•	Use a WeatherAPI para consultar a temperatura atual.
# 	•	Filtre apenas cidades com temperatura entre 18°C e 24°C.
# 	•	Resultado: qual o faturamento total vindo dessas cidades?

def exercicio2():
        path_arquivo_final = "refined/exercicio2/"
        file_name_final = "media_ponderada"
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


        df_resultado = pd.DataFrame([{"faturamento_total_cidades": total_receita_cidades_temp_ameno}])
        df_resultado.to_csv(f"{path_projeto}/{path_arquivo_final}/{file_name_final}.csv", index=False, sep=';')


#exercicio2()




#-----------------------------/////--------------------------------------


#   Exercício 3 – Aluguel de Filmes por Região e População
# 	•	Identifique os países dos clientes com maior número de aluguéis.
# 	•	Use a REST Countries API para obter a população desses países.
# 	•	Calcule o número de aluguéis por 1.000 habitantes.
# 	•	Análise: quais países são mais “cinéfilos” proporcionalmente?

def exercicio3():
        path_arquivo_final = "refined/exercicio3/"
        file_name_final = "paises_ciefilos"

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

        df_final.to_csv(f"{path_projeto}/{path_arquivo_final}/{file_name_final}.csv", index=False, sep=';')

#exercicio3()



#-----------------------------/////--------------------------------------

#   Exercício 4 – Filmes Mais Populares em Cidades Poluídas
# 	•	Liste as 10 cidades com maior número de clientes.
# 	•	Use a AirVisual API para consultar o AQI dessas cidades.
# 	•	Relacione os filmes mais alugados em cidades com AQI > 150.
# 	•	Discussão: poluição impacta preferências de filmes?



def exercicio4_1():
        path_arquivo_final = "refined/exercicio4/"
        file_name_final = "aqi_cidades"

        query_ex4_1 = """
                WITH CTE as (
                        SELECT 
                        city.city as cidade, 
                        count(customer.customer_id) as qtd_clientes
                        FROM customer
                        INNER JOIN address ON customer.address_id = address.address_id 
                        INNER JOIN city    ON address.city_id     = city.city_id 
                        GROUP BY city.city_id
                        ORDER BY qtd_clientes DESC
                        LIMIT 30
                )
                SELECT cidade FROM CTE
        """

        result_query_cidades = run_query(query_ex4_1)

        base_cidades = pd.read_csv(f"{path_projeto}/{path_arquivo_trusted}/{file_name_trusted}.csv", sep=';', usecols=["cidade", "estado", "pais"])

        df_mergeado = pd.merge(result_query_cidades, base_cidades.drop_duplicates(subset=["cidade"]), on="cidade", how="inner")
        

        try:
                df_mergeado["api_resposta"] = df_mergeado.apply(
                        lambda funcao: extract_dados_qualidade_ar_cidade(
                        funcao['cidade'], funcao['estado'], funcao['pais']
                        ),
                        axis=1
                )

                df_mergeado["aqius"] = df_mergeado["api_resposta"].apply(
                                        lambda aqi: (
                                                aqi.get("data", {})
                                                .get("current", {})
                                                .get("pollution", {})
                                                .get("aqius")
                                        ) if isinstance(aqi, dict) else None
                                        )


        except Exception as e:
                print(f"Erro ao processar AQI: {e}")
                return None
        
        df_mergeado[["cidade", "estado", "pais", "aqius"]].to_csv(f"{path_projeto}/{path_arquivo_final}/{file_name_final}.csv", index=False, sep=';')

#exercicio4_1()       


def exercicio4_2():
        path_arquivo_final = "refined/exercicio4/"
        file_name_final = "filmes_mais_alugados"

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
        ORDER BY total_alugueis DESC;

        """
        result_query_filmes = run_query(query_ex4_2)

        result_query_filmes.to_csv(f"{path_projeto}/{path_arquivo_final}/{file_name_final}.csv", index=False, sep=';')

        return None
        


#exercicio4_2()


def analise_resultados():
        path_arquivo_final = "refined/exercicio4/"
        file_name_final = "analise_final"

        aqi_cidades = pd.read_csv(f"{path_projeto}/{path_arquivo_final}/aqi_cidades.csv", sep=';')
        filmes_mais_alugados = pd.read_csv(f"{path_projeto}/{path_arquivo_final}/filmes_mais_alugados.csv", sep=';')

        df_mergeado = pd.merge(aqi_cidades, filmes_mais_alugados, on="cidade", how="inner")

        df_mergeado.to_csv(f"{path_projeto}/{path_arquivo_final}/{file_name_final}.csv", index=False, sep=';')

#analise_resultados()

#-----------------------------/////--------------------------------------


#   Exercício 5 – Clientes em Áreas Críticas
# 	•	Recupere os clientes com endereço em cidades com AQI acima de 130.
# 	•	Combine nome do cliente, cidade, país, temperatura e AQI.
# 	•	Classifique os clientes em “zona de atenção” com base nos critérios ambientais.

# ⸻

def exercicio5():
        path_arquivo_origem = "refined/dados_climaticos/"
        nome_arquivo_origem = "aqi_cidades"

        path_arquivo_final = "refined/exercicio5/"
        file_name_final = "zona_atencao_clientes"

        query_ex5 = """
                SELECT
                        customer.first_name as primeiro_nome,
                        customer.last_name as ultimo_nome,
                        city.city as cidade,
                        address.address as endereco
                FROM customer
                JOIN address ON customer.address_id = address.address_id
                JOIN city ON address.city_id = city.city_id
                JOIN country ON city.country_id = country.country_id;

        """
        result_query_endereco = run_query(query_ex5)

        aqi_cidades = pd.read_csv(f"{path_projeto}/{path_arquivo_origem}/{nome_arquivo_origem}.csv", sep=';')
        
        df_mergeado = pd.merge(
                        result_query_endereco,
                        aqi_cidades,
                        on="cidade",
                        how="left")[["primeiro_nome", "ultimo_nome", "endereco", "cidade", "estado", "pais", "aqius"]]
        
        df_mergeado["classificacao_aqi"] = df_mergeado["aqius"].apply(classificar_aqi)


        df_mergeado.to_csv(f"{path_projeto}/{path_arquivo_final}/{file_name_final}.csv", index=False, sep=';')

        return None

#exercicio5()
#-----------------------------/////--------------------------------------

#   Exercício 6 – Receita por Continente
# 	•	Use a REST Countries API para mapear o continente de cada país.
# 	•	Agrupe a receita total por continente.
# 	•	Exiba os resultados em um gráfico de pizza com matplotlib.


def exercicio_6_1():
        path_arquivo_final = "refined/exercicio6/"
        nome_arquivo_final = "pais_continente"
    
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

        #result_query_receita.to_csv("python/entrega1/data/pais_continente.csv", index=False)
        result_query_receita.to_csv(f"{path_projeto}/{path_arquivo_final}/{nome_arquivo_final}.csv", index=False, sep=';')

        return None      
  
#exercicio_6_1()


def exercicio_6_2():
        path_arquivo_final = "refined/exercicio6/"
        nome_arquivo_final = "pais_continente"

        result_query_receita = pd.read_csv(f"{path_projeto}/{path_arquivo_final}/{nome_arquivo_final}.csv", sep=';')


        df_receita_continente = result_query_receita\
                                .groupby(['continente'])\
                                        .agg(receita_total=('receita_total', 'sum')).reset_index()

        view_plot_pizza(df_receita_continente, 'receita_total', 'continente', 'Receita total por continente' )


#exercicio_6_2() #monta o gráfico de pizza



#-----------------------------/////--------------------------------------

#   Exercício 7 – Tempo Médio de Aluguel vs Clima
# 	•	Calcule o tempo médio de aluguel por cidade (entre rental_date e return_date).
# 	•	Combine com a temperatura atual dessas cidades.
# 	•	Visualize a correlação entre temperatura e tempo médio de aluguel (scatterplot + linha de tendência).


def exercicio_7():

        path_arquivo_origem = "refined/dados_climaticos/"
        nome_arquivo_origem = "clima_cidades"

        query_exec7 = """
        SELECT
        city.city as cidade,
        AVG(EXTRACT(EPOCH FROM (rental.return_date - rental.rental_date))) AS tempo_medio_aluguel_segundos,
        COUNT(rental.rental_id) as num_alugueis_cidade
        FROM rental
        JOIN customer ON rental.customer_id = customer.customer_id
        JOIN address ON customer.address_id = address.address_id
        JOIN city ON address.city_id = city.city_id
        WHERE rental.return_date IS NOT NULL
        GROUP BY city.city
        HAVING COUNT(rental.rental_id) > 20 -- Cidades com pelo menos 20 aluguéis para média mais estável
        ORDER BY city.city;
        """

        result_query_aluguel = run_query(query_exec7)

        result_query_aluguel['tempo_medio_aluguel_dias'] = result_query_aluguel['tempo_medio_aluguel_segundos'] / (60*60*24)

        base_cidades = pd.read_csv(f"{path_projeto}{path_arquivo_origem}{nome_arquivo_origem}.csv", sep=';', usecols=["cidade", "temperatura"])

        df_mergeado = pd.merge(result_query_aluguel, base_cidades.drop_duplicates(subset=["cidade"]), on="cidade", how="inner")

        view_correlacao(df_mergeado)

#exercicio_7()



# ⸻

#   Exercício 8 – Perfil de Clima por Cliente
# 	•	Para cada cliente, crie um perfil com:
# 	•	cidade, temperatura, AQI, total de aluguéis, gasto total.
# 	•	Agrupe os perfis por faixa etária (simulada ou fictícia) e avalie padrões.
# 	•	Objetivo: conectar comportamento de consumo e ambiente.

def exercicio_8():
        path_arquivo_origem = "refined/dados_climaticos/"
        nome_arquivo_origem = "clima_cidades"

        path_arquivo_final = "refined/exercicio8/"
        nome_arquivo_final = "perfil_clientes"

        query_exec8 = """
               SELECT
                customer.customer_id,
                customer.first_name,
                customer.last_name,
                city.city as cidade,
                COUNT(rental.rental_id) AS total_alugueis,
                COALESCE(SUM(payment.amount), 0) AS gasto_total -- COALESCE para clientes sem pagamentos
                FROM customer
                JOIN address ON customer.address_id = address.address_id
                JOIN city ON address.city_id = city.city_id
                LEFT JOIN rental ON customer.customer_id = rental.customer_id
                LEFT JOIN payment ON rental.rental_id = payment.rental_id
                GROUP BY customer.customer_id, customer.first_name, customer.last_name, city.city, address.district
                ORDER BY customer.customer_id;
                """
        result_query_perfil = run_query(query_exec8)    

        base_cidades = pd.read_csv(f"{path_projeto}{path_arquivo_origem}{nome_arquivo_origem}.csv", sep=';', usecols=["cidade", "temperatura"])

        df_mergeado = pd.merge(result_query_perfil, base_cidades.drop_duplicates(subset=["cidade"]), on="cidade", how="inner")

        #como não temos idade da base estou criando uma idade ficticia
        np.random.seed(85)  
        df_mergeado["idade_ficticia"] = np.random.randint(18, 35, size=len(df_mergeado))

        bins = [0, 25, 35, 45, 60, 80]
        labels = ["18-25", "26-35", "36-45", "46-60", "60+"]
        df_mergeado["faixa_etaria"] = pd.cut(df_mergeado["idade_ficticia"], bins=bins, labels=labels, include_lowest=True)

        df_mergeado.to_csv(f"{path_projeto}/{path_arquivo_final}/{nome_arquivo_final}.csv", index=False, sep=';')

#exercicio_8()




# ⸻

#   Exercício 9 – Exportação Inteligente
# 	•	Gere um relatório Excel com os seguintes critérios:
# 	•	Clientes de países com temperatura < 15°C
# 	•	AQI acima de 100
# 	•	Receita individual > média geral
# 	•	Utilize OpenPyXL e organize em múltiplas abas: Clientes, Temperaturas, Alertas.

def exercicio_9():
        path_arquivo_clima = "refined/dados_climaticos/"
        nome_arquivo_clima= "clima_cidades"

        path_arquivo_aqi= "refined/dados_climaticos/"
        nome_arquivo_aqi= "aqi_cidades"

        path_arquivo_final = "refined/exercicio9/"
        nome_arquivo_final = "relatorio_clientes"

        query_exec9_1 = """
        SELECT
                customer.customer_id,
                customer.first_name,
                customer.last_name,
                city.city as cidade,
                address.address,
                address.postal_code
        FROM customer
        JOIN address ON customer.address_id = address.address_id
        JOIN city ON address.city_id = city.city_id
        JOIN country ON city.country_id = country.country_id;
        """
        query_exec9_2 = """
        SELECT 
                city.city as cidade, 
                SUM(payment.amount) AS receita_total
        FROM payment
        JOIN customer ON payment.customer_id = customer.customer_id
        JOIN address ON customer.address_id = address.address_id
        JOIN city ON address.city_id = city.city_id
        GROUP BY city.city
        ORDER BY receita_total DESC;
                """

        result_query_customer = run_query(query_exec9_1) 
        result_query_receita_cidade = run_query(query_exec9_2) 

        base_cidades = pd.read_csv(f"{path_projeto}{path_arquivo_clima}{nome_arquivo_clima}.csv", sep=';', usecols=["cidade", "temperatura"])

        base_cidades_aqi = pd.read_csv(f"{path_projeto}{path_arquivo_aqi}{nome_arquivo_aqi}.csv", sep=';', usecols=["cidade", "aqius"])

        df_mergeado = pd.merge(
                        pd.merge(
                                pd.merge(
                                        result_query_customer, base_cidades, on="cidade", how="inner"),
                                        result_query_receita_cidade, on="cidade", how="inner"),
                                        base_cidades_aqi, on="cidade", how="inner")
        
        media_geral = df_mergeado["receita_total"].mean()

        df_mergeado = df_mergeado[
                        (df_mergeado["temperatura"] < 15) &
                        (df_mergeado["aqius"] > 10) &
                        (df_mergeado["receita_total"] > media_geral)
                        ]
        
        #separand em datasets distintos para cada aba do excel
        df_temperatura = df_mergeado[['first_name', 'cidade', 'temperatura']]
        df_aqi = df_mergeado[['first_name', 'cidade', 'aqius']]
        df_media = df_mergeado[df_mergeado["receita_total"] > media_geral][["first_name", "cidade", "receita_total"]]

        load_data_into_excel(df_temperatura, df_aqi, df_media, path_arquivo_final, nome_arquivo_final) 
       
#exercicio_9()




# ⸻

#   Exercício 10 – API Cache Inteligente (Desafio)
# 	•	Implemente uma lógica que salve os dados de clima e AQI localmente em CSV.
# 	•	Ao consultar novamente a mesma cidade, busque do CSV ao invés da API.
# 	•	Evite chamadas redundantes — bom para práticas de performance e economia de requisições.

#print("Foi desenvolvido em: ingestao_baes e utilizado nos exercícios")

















