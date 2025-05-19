import os
import json
import logging
import requests

from dotenv import load_dotenv
from typing import Optional, Dict

from utils.connect_vault import buscar_secret_value

load_dotenv()

logging.basicConfig(
    level=logging.INFO,  # Pode mudar para DEBUG, WARNING, ERROR dependendo do ambiente
    format="%(asctime)s - %(levelname)s - %(message)s"
)

WEATHER_KEY = buscar_secret_value("api-weather-key")
#AIRVISUAL_KEY = os.getenv("AIRVISUAL_KEY")

pais = "brazil"

print(WEATHER_KEY)
     

# if not WEATHER_KEY:
#     logging.error("Chave da WeatherAPI não encontrada nas variáveis de ambiente.")


# URL_API = 'https://api.weatherapi.com/v1/current.json'
# PARAMETROS = {'q': cidade,'key': WEATHER_KEY}

# try:
#     logging.info(f"Consultando clima para a cidade: {cidade}")    

#     response = requests.get(URL_API, params=PARAMETROS)
#     response.raise_for_status()
#     clima = response.json()


# except requests.exceptions.RequestException as erro:
#     logging.error(f"Erro na consulta da WeatherAPI: {erro}")

   



