from flask import Flask, render_template, jsonify
import paramiko

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

# Rota para a página principal com os botões
@app.route('/')
def index():
    return render_template('index.html')

# Rota que será acionada ao pressionar um botão, executando o script via SSH
@app.route('/executa/<script_name>')
def executa_script(script_name):
    result = executar_script_ssh(script_name)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
