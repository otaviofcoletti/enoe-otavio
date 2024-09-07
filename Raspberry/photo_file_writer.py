import cv2
import time
import os
import json
import logging
from datetime import datetime

# Criar a pasta "logs" se não existir
if not os.path.exists("logs"):
    os.makedirs("logs")
    print("logs directory created.")

# Configuração do logging
logging.basicConfig(
    filename="./logs/photo.log",  # Nome do arquivo de log
    level=logging.ERROR,  # Nível de logging para registrar erros
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato do log
    filemode='a'  # Modo append para evitar sobrescrita
)

# Carregar as configurações do arquivo config.json
try:
    with open("config.json") as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    logging.error(f"Error loading config file: {e}")
    exit(1)

config_camera = config["CAMERA_SETTINGS"]
username = config_camera["username"]
password = config_camera["password"]
ip_camera = config_camera["ip_camera"]

config_capture_interval = config["CAPTURE_INTERVALS"]
capture_interval_seconds = config_capture_interval["capture_interval_seconds"]

# Diretório para salvar as imagens
save_directory = "captured_images"
if not os.path.exists(save_directory):
    os.makedirs(save_directory)
    logging.info("Captured images directory created.")

def capture_picture():
    try:
        # Conectar à câmera IP usando o protocolo RTSP
        stream = cv2.VideoCapture(f'rtsp://{username}:{password}@{ip_camera}')
        ret, frame = stream.read()

        if not ret:
            logging.error("Failed to capture image from the camera.")
            return

        # Criação do nome do arquivo com o timestamp
        filename = f"{datetime.now().strftime('%d-%m-%Y_%H:%M:%S')}.jpg"
        file_path = os.path.join(save_directory, filename)

        # Salvando a imagem com qualidade JPEG padrão
        cv2.imwrite(file_path, frame)

        stream.release()
        cv2.destroyAllWindows()

        logging.info(f"Image saved at {file_path}")
    except Exception as e:
        logging.error(f"Error capturing image: {e}")

def main():
    while True:
        capture_picture()
        time.sleep(capture_interval_seconds)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Program interrupted by user.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
