import RPi.GPIO as GPIO
import time

# Configura o uso do número de pino no modo físico (BCM)
GPIO.setmode(GPIO.BCM)

# Define o pino 15 (GPIO15) como entrada
PIN = 15
GPIO.setup(PIN, GPIO.IN)

try:
    while True:
        # Lê o estado da GPIO 15
        state = GPIO.input(PIN)
        
        if state == GPIO.HIGH:
            print("GPIO 15 está HIGH")
        else:
            print("GPIO 15 está LOW")

            
        GPIO.setup(PIN, GPIO.OUT)
        GPIO.output(PIN, GPIO.LOW)
        
        # Aguarda 1 segundo antes de verificar novamente
        time.sleep(1)

except KeyboardInterrupt:
    print("Teste interrompido pelo usuário")

finally:
    # Limpa as configurações de GPIO ao sair
    GPIO.cleanup()
