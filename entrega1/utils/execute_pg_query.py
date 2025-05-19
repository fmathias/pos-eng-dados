import pandas as pd

from utils.connect_vault import *
from utils.connect_postgres import *

def run_query(query):

    conex = connect_postgres_db()

    return pd.read_sql_query(query, conex)