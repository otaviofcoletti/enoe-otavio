import psycopg2
import time

class DBHandler:
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
                print("Connected to the database successfully.")
                return True
            except psycopg2.OperationalError as e:
                print(f"Failed to connect to the database (attempt {attempt + 1}/{max_retries}): {e}")
                attempt += 1
                time.sleep(retry_delay)
        print("Failed to connect to the database after multiple attempts.")
        return False

    def insert_data(self, epoch, distance):
        try:
            self.cursor.execute(
                "INSERT INTO ultrassonic (epoch, distance) VALUES (%s, %s)",
                (epoch, distance)
            )
            self.conn.commit()
            print(f"Commit done: {epoch}, {distance}")
        except Exception as e:
            print(f"Error inserting data into database: {e}")
            self.conn.rollback()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
