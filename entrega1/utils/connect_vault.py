import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv

load_dotenv()

def buscar_secret_value(nome_secret: str) -> str:
    """
    Busca o valor de um segredo armazenado no Azure Key Vault.

    Args:
        nome_secret (str): Nome do segredo a ser buscado.

    Returns:
        str: Valor do segredo, se encontrado.
    """
    vault = os.getenv("NOME_VAULT")
    vault_url = f"https://{vault}.vault.azure.net/"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)

    return client.get_secret(nome_secret).value