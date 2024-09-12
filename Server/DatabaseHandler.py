import psycopg2
import time
import logging
import paho.mqtt.client as mqtt
import logging


# Configuração do logger para o DatabaseHandler
logger = logging.getLogger('DatabaseHandler')
logger.setLevel(logging.INFO)

handler = logging.FileHandler('./logs/DatabaseHandler.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

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
                logger.info("Connected to the database successfully.")
                return True
            except psycopg2.OperationalError as e:
                logger.error(f"Failed to connect to the database (attempt {attempt + 1}/{max_retries}): {e}")
                attempt += 1
                time.sleep(retry_delay)
        logger.critical("Failed to connect to the database after multiple attempts.")
        return False

    def insert_data(self, table, key, data=None):
        try:
            if table == 'ultrassonic':
                self.cursor.execute(
                    f"INSERT INTO {table} (epoch, distance_cm) VALUES (%s, %s)",
                    (key, data)
                )
                self.conn.commit()
                logger.info(f"Data inserted successfully: epoch={key}, distance_cm={data}")
            elif table == 'images':
                self.cursor.execute(
                    f"INSERT INTO {table} (epoch, image_path) VALUES (%s, %s)",
                    (key, data)
                )
                self.conn.commit()
                logger.info(f"Image inserted successfully: epoch={key}, image_path={data}")
        except Exception as e:
            logger.error(f"Error inserting data into database: {e}")
            self.conn.rollback()

    def close(self):
        if self.cursor:
            self.cursor.close()
            logger.info("Database cursor closed.")
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")
