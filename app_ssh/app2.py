from flask import Flask, render_template, jsonify, Response
import paramiko
import paho.mqtt.client as mqtt
import time
import json
import os
import sys

app = Flask(__name__)


def load_config():
    with open("config.json") as f:
        return json.load(f)

# Função para conectar via SSH e executar o script na Raspberry Pi
def executar_script_ssh(script_name):
    hostname = '100.107.110.8'  # IP do computador remoto
    username = 'intermidia'    # Nome de usuário para conectar
    password = 'Intermidia6205.'  # Senha do usuário

    try:
        # Conectando via SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)

        # Executando o script Python na Raspberry
        stdin, stdout, stderr = ssh.exec_command(f'cd /home/intermidia/enoe-otavio/Raspberry/ && python3 {script_name}.py')
        
        # Capturando a saída do script
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        ssh.close()
        
        if error:
            return {"status": "error", "message": error}
        return {"status": "success", "message": output}

    except Exception as e:
        return {"status": "error", "message": str(e)}

# Função para obter a última mensagem do tópico MQTT
last_ultrasonic_data = ""

def on_message(client, userdata, message):
    global last_ultrasonic_data
    last_ultrasonic_data = message.payload.decode()
    print(f"Received message: {last_ultrasonic_data}")

def get_last_ultrasonic_data():
    config = load_config()
    username = config["CREDENTIALS"]["username"]
    password = config["CREDENTIALS"]["password"]
    broker_address = "100.111.36.103"  # Defina o endereço do seu broker MQTT
    topic = "app/ultrassonic"  # Defina o tópico MQTT apropriado
    client = mqtt.Client()
    client.username_pw_set(username, password)

    client.on_message = on_message
    client.connect(broker_address)
    client.loop_start()
    client.subscribe(topic)

    # Aguardar alguns segundos para obter a mensagem
    client.loop_stop()

    return last_ultrasonic_data

# Função para o streaming de dados
@app.route('/stream')
def stream():
    def event_stream():
        while True:
            data = get_last_ultrasonic_data()  # Obtém a última leitura do sensor
            print(data)
            yield f'data: {data}\n\n'  # Formato de Server-Sent Events
            time.sleep(1)  # Enviar dados a cada 1 segundo

    return Response(event_stream(), mimetype="text/event-stream")

# Rota para a página principal com os botões
@app.route('/')
def index():
    return render_template('index2.html')

# Rota que será acionada ao pressionar um botão, executando o script via SSH
@app.route('/executa/<script_name>')
def executa_script(script_name):
    # Modificando a chamada do script para take_ultrassonic.py
    if script_name == "ultrassonic":
        result = executar_script_ssh('take_ultrassonic')  # Nome do script a ser executado
    else:
        result = executar_script_ssh(script_name)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, threaded=True)
