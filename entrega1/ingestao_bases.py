import os
import time

import pandas as pd
pd.set_option('display.max_colwidth', None)

import pycountry
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

from utils.execute_pg_query import *
from utils.extract import *
from utils.load import *


#   Pré-Tratamento – Realizar a ingestão das bases para consumo interno
# 	•	Ingestão das cidades do banco Pagila
# 	•	Armazenar esses dados internamente para consultar no futuro
# 	•	Download das bases geonames 
# 	•	Padronizar o nome dos paises com as a lib pycountry
# 	•	Buscar a temperatura de todas essas cidades


def extract_load_base_cidades():
        path_destino = "raw/pagila/city"
        file_name = "city"        
     
        query_ingestao_cidade = """
                SELECT city as cidade
                FROM city
                ORDER BY 1;
                """
        result_query = run_query(query_ingestao_cidade)

        load_csv_local_path(result_query, path_destino, file_name)

        return None

#extract_load_base_cidades()


def extract_estados_pais_base_geoname():
        """
        bases utilizadas: 
                https://download.geonames.org/export/dump/admin1CodesASCII.txt
                https://download.geonames.org/export/dump/cities1000.zip

        """
        path_projeto = os.getenv("PATH_PROJETO")
        path_dados_raw = "raw/geonames/state-country"
        file_cities = "cities1000.txt"
        file_codes = "admin1CodesASCII.txt"   

        path_dados_trusted = "trusted/geonames/cidade_estado_pais"
        file_out = "base_cidades.csv"

        df_cidades = pd.read_csv(f"{path_projeto}/{path_dados_raw}/{file_cities}", sep='\t', header=None, low_memory=False)
        df_cidades = df_cidades[[1, 8, 10]]
        df_cidades.columns = ['cidade', 'pais_code', 'estado_code']


        df_estados = pd.read_csv(f"{path_projeto}/{path_dados_raw}/{file_codes}", sep='\t', header=None)
        df_estados = df_estados[[0, 1]] 
        df_estados.columns = ['chave', 'estado']


        df_estados[['pais_code', 'estado_code']] = df_estados['chave'].str.split('.', expand=True)
        df_estados.drop(columns=['chave'], inplace=True)


        df_merged = df_cidades.merge(df_estados, on=['pais_code', 'estado_code'], how='left')

        df_merged.to_csv(f"{path_projeto}/{path_dados_trusted}/{file_out}", index=False, sep=';')

#extract_estados_pais_base_geoname()



def de_para_codigo_nome_pais(code):
    try:
        return pycountry.countries.get(alpha_2=code).name
    except:
        return code


def padroniza_nome_pais():
        path_arquivo = "trusted/geonames/cidade_estado_pais"
        file_name = "base_cidades"   

        path_arquivo_final = "trusted/geonames/cidade_estado_pais"
        file_name_final = "base_cidades_refinada"

        cidades_pagila = pd.read_csv(f"{path_projeto}/{path_arquivo}/{file_name}.csv", sep=';')

        cidades_pagila["pais"] = cidades_pagila["pais_code"].apply(de_para_codigo_nome_pais)

        cidades_pagila.to_csv(f"{path_projeto}/{path_arquivo_final}/{file_name_final}.csv", index=False, sep=';')

        return None  

#padroniza_nome_pais()

def extract_temperatura_cidades():
    import time
    import pandas as pd

    path_arquivo_raw = "raw/pagila/city"
    file_name_raw = "city"

    path_arquivo_trusted = "trusted/geonames/cidade_estado_pais"
    file_name_trusted = "base_cidades_refinada"

    path_arquivo_final = "refined/dados_climaticos"
    file_name_final = "clima_cidades"

    base_cidades_geonomes = pd.read_csv(f"{path_projeto}/{path_arquivo_trusted}/{file_name_trusted}.csv", sep=';')
    base_cidades_pagila = pd.read_csv(f"{path_projeto}/{path_arquivo_raw}/{file_name_raw}.csv", sep=';')

    df_mergeado = pd.merge(base_cidades_geonomes, base_cidades_pagila, on="cidade", how="inner")
    df_mergeado = df_mergeado.drop_duplicates(subset=["cidade", "estado", "pais"])

    #print(df_mergeado)

    temperaturas = []

    for _, row in df_mergeado.iterrows():
        cidade = row["cidade"]

        try:
            clima = extract_dados_clima(cidade)
            time.sleep(1)

            if clima and "current" in clima:
                temperatura_cidade = clima["current"]["temp_c"]

                temperaturas.append({
                    "cidade": cidade,
                    "estado": row["estado"],
                    "pais": row["pais"],
                    "temperatura": temperatura_cidade,
                    "sensacao_termica": clima["current"]["feelslike_c"],
                    "condicao": clima["current"]["condition"]["text"]
                })

        except Exception as e:
            print(f"Erro ao buscar temperatura para {cidade}: {e}")

    # Cria DataFrame e salva resultado
    df_temperaturas = pd.DataFrame(temperaturas)
    df_temperaturas.to_csv(f"{path_projeto}/{path_arquivo_final}/{file_name_final}.csv", index=False, sep=';')

#extract_temperatura_cidades()


def extract_aqi_cidades():        

        path_arquivo_refined = "refined/dados_climaticos"
        file_name_refined = "clima_cidades"

        path_arquivo_final = "refined/dados_climaticos"
        file_name_final = "aqi_cidades"
        path_completo = f"{path_projeto}/{path_arquivo_final}/{file_name_final}.csv"

        base_clima = pd.read_csv(
                f"{path_projeto}/{path_arquivo_refined}/{file_name_refined}.csv",
                sep=';'
        )

        if os.path.exists(path_completo):
                base_aqi_existente = pd.read_csv(path_completo, sep=';')
        else:
                base_aqi_existente = pd.DataFrame(columns=["cidade", "estado", "pais", "aqius"])

                with open(path_completo, mode='w', encoding='utf-8', newline='') as f:
                        base_aqi_existente.to_csv(f, index=False, sep=';')

        cidades_faltando = pd.merge(
                base_clima,
                base_aqi_existente[["cidade", "estado", "pais"]].drop_duplicates(),
                on=["cidade", "estado", "pais"],
                how="left",
                indicator=True
                )

        cidades_faltando = cidades_faltando[cidades_faltando["_merge"] == "left_only"].drop(columns=["_merge"])

        print(f"{len(cidades_faltando)} cidades ainda não têm AQI, consultando API...")

        for _, row in cidades_faltando.iterrows():
                cidade = row["cidade"]
                estado = row["estado"]
                pais = row["pais"]

                try:
                        resposta = extract_dados_qualidade_ar_cidade(cidade, estado, pais)
                        time.sleep(10)

                        aqius = (
                                resposta.get("data", {})
                                .get("current", {})
                                .get("pollution", {})
                                .get("aqius")
                                ) if isinstance(resposta, dict) else None

                except Exception as e:
                        print(f"Erro ao buscar AQI para {cidade}: {e}")
                        aqius = None

                df_linha = pd.DataFrame([{
                        "cidade": cidade,
                        "estado": estado,
                        "pais": pais,
                        "aqius": aqius
                }])

                with open(path_completo, mode='a', encoding='utf-8', newline='') as f:
                        df_linha.to_csv(f, index=False, header=False, sep=';')

extract_aqi_cidades()