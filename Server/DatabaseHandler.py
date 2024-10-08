import psycopg2
import time
import paho.mqtt.client as mqtt
from LoggingClass import Logger  # Certifique-se de que o caminho para a classe Logger está correto

# Configuração do logger para o DatabaseHandler usando a classe Logger
db_logger = Logger('DatabaseHandler', rotation='W0').get_logger()  # Rotação semanal

class DatabaseHandler:
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None
        self.cursor = None

    def connect(self, max_retries=5, retry_delay=5):
        attempt = 0
        while attempt < max_retries:
            try:
                self.conn = psycopg2.connect(**self.db_config)
                self.cursor = self.conn.cursor()
                db_logger.info("Connected to the database successfully.")
                return True
            except psycopg2.OperationalError as e:
                db_logger.error(f"Failed to connect to the database (attempt {attempt + 1}/{max_retries}): {e}")
                attempt += 1
                time.sleep(retry_delay)
        db_logger.critical("Failed to connect to the database after multiple attempts.")
        return False

    def insert_data(self, table, key, data=None):
        try:
            if table == 'ultrassonic':
                self.cursor.execute(
                    f"INSERT INTO {table} (epoch, distance_cm) VALUES (%s, %s)",
                    (key, data)
                )
                self.conn.commit()
                db_logger.info(f"Data inserted successfully: epoch={key}, distance_cm={data}")
            elif table == 'images':
                self.cursor.execute(
                    f"INSERT INTO {table} (epoch, image_path) VALUES (%s, %s)",
                    (key, data)
                )
                self.conn.commit()
                db_logger.info(f"Image inserted successfully: epoch={key}, image_path={data}")
            elif table == 'raspberry_info':
                # Certifique-se de que `data` é um dicionário com os valores corretos
                cpu_temperature = data.get('cpu_temperature')
                cpu_usage = data.get('cpu_usage')
                ram_usage = data.get('ram_usage')
                storage_usage = data.get('storage_usage')

                # Execute o comando SQL para inserir os dados da Raspberry Pi
                self.cursor.execute(
                    f"INSERT INTO {table} (epoch, cpu_temperature, cpu_usage, ram_usage, storage_usage) VALUES (%s, %s, %s, %s, %s)",
                    (key, cpu_temperature, cpu_usage, ram_usage, storage_usage)
                )
                self.conn.commit()
                db_logger.info(f"Raspberry info inserted successfully: epoch={key}, cpu_temperature={cpu_temperature}, cpu_usage={cpu_usage}, ram_usage={ram_usage}, storage_usage={storage_usage}")
        except Exception as e:
            db_logger.error(f"Error inserting data into database: {e}")
            self.conn.rollback()

    def close(self):
        if self.cursor:
            self.cursor.close()
            db_logger.info("Database cursor closed.")
        if self.conn:
            self.conn.close()
            db_logger.info("Database connection closed.")
