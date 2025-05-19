import json
from azure.storage.filedatalake import DataLakeServiceClient
from utils.connect_vault import buscar_secret_value

ADLS_KEY = buscar_secret_value("adls-key")
ADLS_NAME = buscar_secret_value("adls-name")
CONTAINER_NAME = "python"


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
