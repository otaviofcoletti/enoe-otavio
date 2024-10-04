from LoggingClass import Logger  # Certifique-se de que o caminho para a classe Logger está correto
import serial

"""
UltrassonicClass is a class to interface with an ultrasonic sensor via a serial port.

Attributes:
    serialportname (str): The name of the serial port to use.
    baudrate (int): The baud rate for the serial communication.
    ser (serial.Serial): The serial connection object.

Methods:
    set_serial():
        Opens the serial port with the specified settings.
        Returns:
            serial.Serial: The opened serial connection.
        Raises:
            serial.SerialException: If there is an error opening the serial port.

    get_line():
        Reads a line of data from the serial port, processes it, and returns it as an integer.
        Returns:
            int: The processed data from the serial port.
            None: If there is an error reading from the serial port.
"""

logger = Logger('UltrassonicClass', rotation='W0').get_logger()  # Rotação semanal

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
            #print(line)
            return int(line)
        except Exception as e:
            logger.error(f"Error reading from serial port: {e}")
            return None
