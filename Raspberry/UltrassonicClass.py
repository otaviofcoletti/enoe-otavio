import logging
import serial

# Configuração do logging no modo append
logging.basicConfig(
    filename='./logs/ultrassonic.log',  # Nome do arquivo de log
    level=logging.INFO,  # Nível de logging
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato do log
    filemode='a'  # Modo append (anexar ao arquivo existente)
)

class UltrassonicClass:
    def __init__(self, serialportname='/dev/ttyS0', baudrate=9600):
        self.serialportname = serialportname
        self.baudrate = baudrate
        self.ser = None

    def set_serial(self):
        try:
            self.ser = serial.Serial(self.serialportname, self.baudrate)
            logging.info("Serial port opened successfully.")
            return self.ser
        except serial.SerialException as e:
            logging.error(f"Error opening serial port: {e}")
            exit(1)

    def get_line(self):
        try:
            self.ser.reset_input_buffer()
            line = self.ser.read(6).decode().strip().replace("R", "")
            #print(line)
            return int(line)
        except Exception as e:
            logging.error(f"Error reading from serial port: {e}")
            return None
