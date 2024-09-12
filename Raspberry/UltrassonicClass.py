import logging
import serial

# Configuração do logging no modo append
logger = logging.getLogger('UltrassonicClass')
logger.setLevel(logging.INFO)

handler = logging.FileHandler('./logs/UltrassonicClass.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class UltrassonicClass:
    def __init__(self, serialportname='/dev/ttyS0', baudrate=9600):
        self.serialportname = serialportname
        self.baudrate = baudrate
        self.ser = None

    def set_serial(self):
        try:
            self.ser = serial.Serial(self.serialportname, self.baudrate)
            logger.info("Serial port opened successfully.")
            return self.ser
        except serial.SerialException as e:
            logger.error(f"Error opening serial port: {e}")
            exit(1)

    def get_line(self):
        try:
            self.ser.reset_input_buffer()
            line = self.ser.read(6).decode().strip().replace("R", "")
            print(line)
            return int(line)
        except Exception as e:
            logger.error(f"Error reading from serial port: {e}")
            return None
