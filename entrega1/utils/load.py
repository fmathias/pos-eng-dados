import os
import json
import pandas as pd
from dotenv import load_dotenv
from azure.storage.filedatalake import DataLakeServiceClient

#from utils.connect_vault import buscar_secret_value

# Carregar variáveis de ambiente
load_dotenv()

#ADLS_KEY = buscar_secret_value("adls-key")
#ADLS_NAME = buscar_secret_value("adls-name")
CONTAINER_NAME = "python"

path_projeto = os.getenv("PATH_PROJETO")

def connect_adls(file_name: str, path_name: str):
    service_client = DataLakeServiceClient(
        account_url=f"https://{ADLS_NAME}.dfs.core.windows.net",
        credential=ADLS_KEY
    )

    fs_client = service_client.get_file_system_client(file_system=CONTAINER_NAME)
    dir_client = fs_client.get_directory_client(path_name)
    dir_client.create_directory()

    file_client = dir_client.create_file(file_name)
    return file_client

def load_json_to_adls_datalake(json_data: dict, file_name: str, path_name: str):
    file_client = connect_adls(file_name, path_name)

    json_string = json.dumps(json_data, indent=2, ensure_ascii=False)
    file_client.append_data(json_string, offset=0, length=len(json_string))
    file_client.flush_data(len(json_string))

    return None

def load_csv_local_path(data, path, file_name):

    data.to_csv(f'{path_projeto}/{path}/{file_name}.csv', index=False, sep=";", encoding="utf-8")

    return None



# def load_dados_adls(nome_arquivo, extensao_arquivo):
#     """
#     Carrega os dados no ADLS.

#     Args:
#         nome_arquivo (str): Nome do arquivo de onde os dados serão carregados.

#     Returns:
#         dict | None: Dados carregados ou None se falhar.
#     """


#     try:
#         with open(nome_arquivo, "r", encoding="utf-8") as arquivo:
#             dados = json.load(arquivo)
#         return dados
#     except Exception as e:
#         print(f"Erro ao carregar dados: {e}")
#         return None


def load_data_into_excel(df_temperatura, df_aqi, df_media, path_arquivo_final, nome_arquivo_final ):
    import openpyxl
    from openpyxl.utils.dataframe import dataframe_to_rows
    from openpyxl import Workbook

    wb = Workbook()

    ws1 = wb.active
    ws1.title = "TEMPERATURA"
    for r in dataframe_to_rows(df_temperatura, index=False, header=True):
        ws1.append(r)

    # Aba 2: Temperaturas de todas as cidades
    ws2 = wb.create_sheet("AQI")
    for r in dataframe_to_rows(df_aqi, index=False, header=True):
        ws2.append(r)

    # Aba 3: Cidades com AQI > 100
    ws3 = wb.create_sheet("Alertas")
    for r in dataframe_to_rows(df_media, index=False, header=True):
        ws3.append(r)

    # Salva o arquivo
    caminho_final = f"{path_projeto}{path_arquivo_final}{nome_arquivo_final}.xlsx"
    wb.save(caminho_final)

