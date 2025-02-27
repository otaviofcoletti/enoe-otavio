import cv2
import os
import json
import logging
from datetime import datetime



from LoggingClass import Logger  # Certifique-se de que o caminho para a classe Logger está correto

logger = Logger('take_photo', rotation='W0').get_logger()  # Rotação semanal

# Carregar as configurações do arquivo config.json
try:
    with open("config.json") as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    logger.error(f"Error loading config file: {e}")
    exit(1)

config_camera = config["CAMERA_SETTINGS"]
username = config_camera["username"]
password = config_camera["password"]
ip_camera = config_camera["ip_camera"]

# Diretório para salvar as imagens
save_directory = "data_images"
if not os.path.exists(save_directory):
    os.makedirs(save_directory)
    logger.info("Captured images directory created.")

def capture_picture():
    try:
        # Conectar à câmera IP usando o protocolo RTSP
        stream = cv2.VideoCapture(f'rtsp://{username}:{password}@{ip_camera}')

        ret, frame = stream.read()

        if not ret:
            logger.error("Failed to capture image from the camera.")
            return

        # Criação do nome do arquivo com o timestamp
        filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
        file_path = os.path.join(save_directory, filename)

        # The image is saved as a JPEG with a specified quality level of 60.
        height, width, layers = frame.shape
        frame = cv2.resize(frame, (width // 2, height // 2))
        jpeg_quality = 50
        cv2.imwrite(file_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
        stream.release()
        cv2.destroyAllWindows()

        logger.info(f"Image saved at {file_path}")
    except Exception as e:
        logger.error(f"Error capturing image: {e}")

if __name__ == "__main__":
    try:
        capture_picture()
        logger.info("Image captured successfully, program will now exit.")
        print("Foto tirada")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
