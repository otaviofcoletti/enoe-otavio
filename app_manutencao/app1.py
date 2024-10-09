import paramiko
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# Função para conectar via SSH e executar o script na Raspberry Pi
def executar_script_ssh(script_name):
    hostname = '100.107.110.8'  # IP do computador remoto
    username = 'intermidia'    # Nome de usuário para conectar
    password = 'Intermidia6205.'      # Senha do usuário

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

# Defina o caminho para a pasta que contém as imagens
IMAGE_FOLDER = '/home/intermidia/enoe-otavio/Server/images'

def get_all_images():
    images = []
    for root, dirs, files in os.walk(IMAGE_FOLDER):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                filepath = os.path.join(root, filename)
                mod_time = os.path.getmtime(filepath)
                date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d')
                relative_path = os.path.relpath(filepath, IMAGE_FOLDER)
                images.append({
                    'filename': filename,
                    'mod_time': mod_time,
                    'date': date,
                    'relative_path': relative_path.replace('\\', '/')
                })
    images.sort(key=lambda x: x['mod_time'], reverse=True)
    return images

# Rota que será acionada ao pressionar um botão, executando o script via SSH
@app.route('/executa/<script_name>')
def executa_script(script_name):
    result = executar_script_ssh(script_name)

    return jsonify(result)

# Rota para servir imagens do diretório de imagens
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

# Variável para armazenar a última imagem exibida
last_image = None

@app.route('/')
def index():
    global last_image
    images = get_all_images()
    last_image = images[0]
    if not images:
        return "Nenhuma imagem encontrada."
    index = int(request.args.get('index', 0))
    if index < 0:
        index = 0
    elif index >= len(images):
        index = len(images) - 1
    image = images[index]
    return render_template('index.html', image=image, index=index, total=len(images))



# Função para obter a última imagem
def get_latest_image():
    images = get_all_images()
    if images:
        return images[0]  # A mais recente será a primeira na lista (ordenada por mod_time)
    return None

# Rota para verificar se há uma nova imagem
@app.route('/check_new_image')
def check_new_image():
    global last_image
    latest_image = get_latest_image()
    
    # Se não houver nenhuma imagem ainda
    if not latest_image:
        return jsonify({"new_image_available": False})

    # Se for a primeira verificação ou uma nova imagem foi adicionada
    if last_image is None or latest_image['filename'] != last_image['filename']:
        last_image = latest_image
        return jsonify({"new_image_available": True, "new_image_url": latest_image['relative_path']})

    # Nenhuma nova imagem detectada
    return jsonify({"new_image_available": False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
