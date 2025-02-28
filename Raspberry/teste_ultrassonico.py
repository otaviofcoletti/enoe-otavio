import serial
import time
import logging

logging.basicConfig(level=logging.DEBUG)

def get_line(ser):
    try:
        # Tenta ler 6 bytes com timeout
        data = ser.read(6)
        if not data:
            logging.warning("Nenhum dado recebido.")
            return ""
        return data.decode().strip().replace("R", "")
    except Exception as e:
        logging.error(f"Erro ao ler dados: {e}")
        return ""

def main():
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    time.sleep(2)  # Tempo para estabilizar a conexão
    while True:
        line = get_line(ser)
        if line:
            print(line)
        time.sleep(0.1)

if __name__ == '__main__':
    main()
