import os
import json
import logging
import pandas as pd
import requests

from dotenv import load_dotenv
from typing import Optional, Dict
from datetime import datetime

from utils.extract import *
from utils.transform import *
from utils.load import *

# def main(cidade):
#     try:
#         dados_clima = extract_dados_clima(cidade)

#         dados_pais_cidade_buscada = dados_clima["location"]["country"]
#         dados_estado_cidade_buscada = dados_clima["location"]["region"]

#         dados_qualidade_ar_estado = extract_dados_estados_qualidade_ar(dados_pais_cidade_buscada)
#         dados_qualidade_ar_cidade = extract_dados_qualidade_ar_cidade(cidade, dados_estado_cidade_buscada, dados_pais_cidade_buscada)
#         #infos_pais = busca_dados_pais_por_nome(pais_cidade_buscada)
        
#         dados = processar_dados_cidade(cidade, dados_clima, dados_qualidade_ar_estado, dados_qualidade_ar_cidade)

#         print(json.dumps(dados, indent=4, ensure_ascii=False))
#     except Exception as e:
#         print(f"Erro ao buscar dados de qualidade do ar: {e}")
#         return None





def main(cidade):
    """
    EXTRACTS
    """

    try:        
        
        clima = extract_dados_clima(cidade)
        pais = clima["location"]["country"]
        estado = clima["location"]["region"]

        qualidade_estado = extract_dados_estados_qualidade_ar(pais)
        qualidade_cidade = extract_dados_qualidade_ar_cidade(cidade, estado, pais)      

    except Exception as e:
        print(f"Erro ao extrair os dados: {e}")
        return None    

    """
    TRANFORMS
    """
    try:
               
        dados_json = processar_dados_cidade(clima, qualidade_estado, qualidade_cidade, cidade)
        
    except Exception as e:
        print(f"Erro ao transformar os dados: {e}")
        return None  
    
    """
    LOAD
    """
    tipo_dado = "clima"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    data_carga = datetime.now().strftime("%Y-%m-%d")

    file_name = f"{cidade}_{tipo_dado}_{timestamp}.json"
    path_name = f"{tipo_dado}/{data_carga}"
    
    try:
        load_json_to_adls_datalake(dados_json, file_name, path_name)

    except Exception as e:
        print(f"Erro ao carregar os dados: {e}")
        return None

main("Rio de Janeiro") 