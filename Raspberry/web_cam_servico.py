import cv2
import time
import os
import json
import logging
from datetime import datetime

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Caminho da pasta onde as fotos serão salvas
pasta_destino = "/home/intermidia/enoe-otavio/Raspberry/webcam_fotos"
os.makedirs(pasta_destino, exist_ok=True)

# Arquivo de metadados onde serão armazenadas as informações das fotos
arquivo_metadata = os.path.join(pasta_destino, 'metadata.json')

# Inicializa a lista de metadados
metadata = []

# Inicializa a captura da webcam (índice 0; ajuste se necessário)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    logging.error("Erro: Não foi possível acessar a webcam.")
    exit()

# Aguarda alguns segundos para que a câmera se estabilize
time.sleep(2)

contador = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            logging.error("Erro: Não foi possível capturar a imagem.")
            break

        # Cria um timestamp e define o nome do arquivo
        agora = datetime.now()
        timestamp_str = agora.strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"foto_{timestamp_str}_{contador}.jpg"
        caminho_imagem = os.path.join(pasta_destino, nome_arquivo)
        
        # Salva a imagem
        cv2.imwrite(caminho_imagem, frame)
        logging.info(f"Imagem salva como {caminho_imagem}")

        # Adiciona os dados da foto à lista de metadados
        metadata.append({
            "arquivo": nome_arquivo,
            "timestamp": agora.isoformat()
        })
        
        # Salva (ou atualiza) os metadados em um arquivo JSON
        with open(arquivo_metadata, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        contador += 1
        # Aguarda 2 segundos entre as capturas (pode ajustar conforme necessário)
        time.sleep(2)

except KeyboardInterrupt:
    logging.info("Captura interrompida pelo usuário.")

finally:
    cap.release()
    logging.info("Webcam liberada e aplicação finalizada.")
