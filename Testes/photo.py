import cv2
import time
import os
from datetime import datetime

# Configurações da câmera IP
username = 'admin'
password = 'admin'
ip_camera = '10.1.1.11'

# Diretório para salvar as imagens
save_directory = "data/images"
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

def capture_picture():
    stream = cv2.VideoCapture(f'rtsp://{username}:{password}@{ip_camera}')
    ret, frame = stream.read()
    
    if not ret:
        print("Falha ao capturar imagem.")
        return

    # Criação do nome do arquivo com o timestamp
    filename = f"{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.jpg"
    file_path = os.path.join(save_directory, filename)

    # Salvando a imagem com qualidade JPEG padrão
    cv2.imwrite(file_path, frame)

    stream.release()
    cv2.destroyAllWindows()

    print(f"Imagem salva em {file_path}")

try:
    while True:
        capture_picture()
        time.sleep(5)  # Captura uma imagem a cada 5 segundos
except Exception as e:
    print("Erro:", e)
