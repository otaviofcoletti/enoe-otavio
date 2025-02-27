import psycopg2
import pandas as pd

# Conectar ao banco
conn = psycopg2.connect(
    dbname="enoe_database",
    user="user",
    password="password",
    host="172.18.0.2",
    port="5432"
)

# Definir a consulta SQL ultrasonic, weather, raspberry_info
query = "SELECT * FROM weather;"

# Ler os dados e exportar para CSV
df = pd.read_sql(query, conn)
df.to_csv("weather.csv", index=False)

# Fechar conexão
conn.close()
