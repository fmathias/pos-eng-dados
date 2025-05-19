import psycopg2

from utils.connect_vault import buscar_secret_value

user = buscar_secret_value("pg-aula-user")
password = buscar_secret_value("pg-aula-password")
host = buscar_secret_value("pg-aula-host")
db = buscar_secret_value("pg-aula-db")

#print(user, password, host, db)

def connect_postgres_db():

    pg_engine = psycopg2.connect(f"postgresql://{user}:{password}@{host}/{db}?sslmode=require")

    return pg_engine