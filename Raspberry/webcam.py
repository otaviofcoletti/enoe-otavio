import cv2
import time

# Inicializa a captura da webcam (índice 0; se houver mais de uma, ajuste conforme necessário)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro: Não foi possível acessar a webcam.")
    exit()

# Aguarda um pouco para que a câmera se estabilize (exposição, foco, etc.)
time.sleep(2)

# Captura um frame da webcam
ret, frame = cap.read()

if not ret:
    print("Erro: Não foi possível capturar a imagem.")
else:
    # Exibe a imagem capturada em uma janela
    
    # Salva a imagem em um arquivo
    cv2.imwrite('foto_webcam.jpg', frame)
    print("Imagem salva como foto_webcam.jpg")
    
    # Aguarda até que uma tecla seja pressionada para fechar a janela
    cv2.waitKey(0)

# Libera a câmera e fecha todas as janelas abertas
cap.release()
cv2.destroyAllWindows()
