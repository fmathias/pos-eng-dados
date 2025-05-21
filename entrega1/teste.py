import os
import ast


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

def exercicio5():
    query_ex5 = """"
    
    
    """





    return None
