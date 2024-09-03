import json
from mqtt_handler import MQTTClientHandler
from db_handler import DBHandler
import time

def load_config():
    with open("config.json") as f:
        return json.load(f)

def main():
    config = load_config()

    mqtt_config = config["MQTT"]
    broker_endpoint = mqtt_config["broker_endpoint"]
    topic = "paho/test/topic"

    db_config = config["DATABASE"]

    username = config["CREDENTIALS"]["username"]
    password = config["CREDENTIALS"]["password"]

    db_handler = DBHandler(db_config)
    if db_handler.connect():
        mqtt_handler = MQTTClientHandler(broker_endpoint, topic, db_handler, username, password)

        try:
            mqtt_handler.connect_and_listen()
        except KeyboardInterrupt:
            print("Interrupted by user.")
            mqtt_handler.disconnect()
        finally:
            db_handler.close()
    else:
        print("Database connection failed. Retrying in 10 seconds...")
        time.sleep(10)
        main()  # Retry the connection by calling main again

if __name__ == "__main__":
    main()
