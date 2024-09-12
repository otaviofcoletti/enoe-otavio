import psutil
import time
import requests

def monitor_network_usage(interval=5):
    # Captura os contadores de I/O de rede iniciais
    net_before = psutil.net_io_counters()

    # Realiza um GET request ao Google
    response = requests.get('https://www.google.com')

    # Captura os contadores de I/O de rede após o request
    net_after = psutil.net_io_counters()

    # Calcula o uso de dados (em bytes) no intervalo de tempo
    sent_bytes = net_after.bytes_sent - net_before.bytes_sent
    received_bytes = net_after.bytes_recv - net_before.bytes_recv

    print(f"GET request status: {response.status_code}")
    print(f"Dados enviados: {sent_bytes / 1024:.2f} KB")
    print(f"Dados recebidos: {received_bytes / 1024:.2f} KB")

# Monitora o uso de rede para um GET request ao Google
monitor_network_usage()
