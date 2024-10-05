import paramiko

def ssh_connect(hostname, username, password, command):
    try:
        # Criando um cliente SSH
        ssh = paramiko.SSHClient()

        # Carregar as chaves do host (se for a primeira vez, aceitará o host automaticamente)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Conectar ao servidor SSH
        ssh.connect(hostname, username=username, password=password)

        # Executar o comando remoto
        stdin, stdout, stderr = ssh.exec_command(command)

        # Ler a saída do comando
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        if output:
            print(f"Output:\n{output}")
        if error:
            print(f"Error:\n{error}")

    except Exception as e:
        print(f"Falha na conexão SSH: {str(e)}")

    finally:
        # Fechar a conexão SSH
        ssh.close()

# Exemplo de uso
hostname = '100.107.110.8'  # IP do computador remoto
username = 'intermidia'    # Nome de usuário para conectar
password = 'Intermidia6205.'      # Senha do usuário
command = 'ls'              # Comando que será executado no computador remoto

ssh_connect(hostname, username, password, command)
