import psycopg2
import time
import logging

class DatabaseHandler:
    def __init__(self, db_config, log_file='logs/database.log', append_log=True):
        self.db_config = db_config
        self.conn = None
        self.cursor = None

        # Configurar logging
        self.setup_logging(log_file, append_log)

    def setup_logging(self, log_file, append_log):
        log_mode = 'a' if append_log else 'w'
        logging.basicConfig(filename=log_file, filemode=log_mode, level=logging.DEBUG,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def connect(self, max_retries=5, retry_delay=5):
        attempt = 0
        while attempt < max_retries:
            try:
                self.conn = psycopg2.connect(**self.db_config)
                self.cursor = self.conn.cursor()
                self.logger.info("Connected to the database successfully.")
                return True
            except psycopg2.OperationalError as e:
                self.logger.error(f"Failed to connect to the database (attempt {attempt + 1}/{max_retries}): {e}")
                attempt += 1
                time.sleep(retry_delay)
        self.logger.critical("Failed to connect to the database after multiple attempts.")
        return False

    def insert_data(self, epoch, distance):
        try:
            self.cursor.execute(
                "INSERT INTO ultrassonic (epoch, distance) VALUES (%s, %s)",
                (epoch, distance)
            )
            self.conn.commit()
            self.logger.info(f"Data inserted successfully: epoch={epoch}, distance={distance}")
        except Exception as e:
            self.logger.error(f"Error inserting data into database: {e}")
            self.conn.rollback()

    def close(self):
        if self.cursor:
            self.cursor.close()
            self.logger.info("Database cursor closed.")
        if self.conn:
            self.conn.close()
            self.logger.info("Database connection closed.")
