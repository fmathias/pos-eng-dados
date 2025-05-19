import os
import logging
import requests

from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Optional, Dict

from utils.connect_vault import buscar_secret_value

load_dotenv()

logging.basicConfig(
    level=logging.INFO,  # Opções DEBUG, WARNING, ERROR
    format="%(asctime)s - %(levelname)s - %(message)s"
)

WEATHER_KEY = buscar_secret_value("api-weather-key")


def extract_dados_clima(cidade: str) -> Optional[Dict]:    

    if not WEATHER_KEY:
        logging.error("Chave da WeatherAPI não encontrada nas variáveis de ambiente.")
        return None

    URL_API = 'https://api.weatherapi.com/v1/current.json'
    PARAMETROS = {'q': cidade,'key': WEATHER_KEY}

    try:
        logging.info(f"Consultando clima para a cidade: {cidade}")    

        response = requests.get(URL_API, params=PARAMETROS)
        response.raise_for_status()
        clima = response.json()

        return clima

    except requests.exceptions.RequestException as erro:
        logging.error(f"Erro na consulta da WeatherAPI: {erro}")
        return None


def extract_dados_paises_qualidade_ar() -> Optional[Dict]:
    AIRVISUAL_KEY = buscar_secret_value("api-airvisual-key")

    if not AIRVISUAL_KEY:
        logging.error("Chave da AirVisualAPI não encontrada nas variáveis de ambiente.")
        return None

    URL_API = 'http://api.airvisual.com/v2/countries'
    PARAMETROS = {'key': AIRVISUAL_KEY}

    try:
        logging.info("Consultando lista de paises disponíveis na API")    

        response = requests.get(URL_API, params=PARAMETROS)
        response.raise_for_status()
        paises = response.json()

        return paises

    except requests.exceptions.RequestException as erro:
        logging.error(f"Erro na consulta da AirVisualAPI: {erro}")
        return None


def extract_dados_estados_qualidade_ar(pais: str) -> Optional[Dict]:
    AIRVISUAL_KEY = buscar_secret_value("api-airvisual-key")

    if not AIRVISUAL_KEY:
        logging.error("Chave da AirVisualAPI não encontrada nas variáveis de ambiente.")
        return None
    
    URL_API = 'http://api.airvisual.com/v2/states'
    PARAMETROS = {'country':pais,'key': AIRVISUAL_KEY}

    try:
        logging.info("Consultando lista de Estados disponíveis para o País selecionado")    

        response = requests.get(URL_API, params=PARAMETROS)
        response.raise_for_status()
        estados = response.json()

        return estados
    
    except requests.exceptions.RequestException as erro:
        logging.error(f"Erro na consulta da AirVisualAPI: {erro}")
        return None


 
def extract_dados_qualidade_ar_cidade(cidade, estado, pais):
    AIRVISUAL_KEY = buscar_secret_value("api-airvisual-key")

    if not WEATHER_KEY:
        logging.error("Chave da WeatherAPI não encontrada nas variáveis de ambiente")
        return None

    URL_API = 'http://api.airvisual.com/v2/city'
    PARAMETROS = {'city': cidade, 'state':estado, 'country':pais, 'key': AIRVISUAL_KEY}

    try:
        logging.info(f"Consultando clima para a cidade: {cidade}")    

        response = requests.get(URL_API, params=PARAMETROS)
        response.raise_for_status()
        clima = response.json()

        return clima

    except requests.exceptions.RequestException as erro:
        logging.error(f"Erro na consulta da WeatherAPI: {erro}")

        return None

  


def extract_dados_pais_por_nome(pais) -> Optional[Dict]:

    URL_API = f'https://restcountries.com/v3.1/name/{pais}'

    try:
        logging.info("Consultando informações disponíveis na API")    

        response = requests.get(URL_API)
        response.raise_for_status()
        info_pais = response.json()

        return info_pais

    except requests.exceptions.RequestException as erro:
        logging.error(f"Erro na consulta da API: {erro}")
        return None


def extract_dados_previsao_tempo(cidade, data):
    """
    Consulta a previsão do tempo para uma cidade utilizando a WeatherAPI.

    Args:
        cidade (str): O nome da cidade para a qual a previsão será consultada.

    Returns:
        dict | None: Dados da previsão ou None se falhar.
    """
    try:
        # Date between 14 days and 300 days from today in the future in yyyy-MM-dd format
        data_minima = datetime.today() + timedelta(days=14)
        data_maxima = datetime.today() + timedelta(days=300)
        data_formatada = datetime.strptime(data, "%Y-%m-%d")

        if not (data_minima <= data_formatada <= data_maxima):
            raise ValueError("A data deve estar entre 14 e 300 dias a partir de hoje.")
        resposta = requests.get(
            f"http://api.weatherapi.com/v1/future.json?key={WEATHER_KEY}&q={cidade}&dt={data_formatada}"
        )
        resposta.raise_for_status()

        return resposta.json()
    
    except Exception as e:
        print(f"Erro ao buscar previsão do tempo: {e}")
        return None
