import subprocess
import os
import datetime
import shutil
import time
# Configurações

## Como restaurar backup
#https://www.youtube.com/watch?v=57FW16QvFJ8&ab_channel=CodeTotal


CONTAINER_NAME = "postgres"  # Nome do container Docker do PostgreSQL
DB_USER = "user"             # Usuário do PostgreSQL
DB_NAME = "ultrassonic_sensor"  # Nome do banco de dados
BACKUP_DIR = "/home/intermidia/enoe-otavio/Database/backups"  # Diretório de backup no host
RCLONE_REMOTE = "gdrive:backup-folder"  # Nome do remote rclone

# Função para criar o backup
def create_backup():
    # Cria o diretório de backup se não existir
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    # Nome do arquivo de backup com data atual
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{current_date}.sql.gz")

    # Comando para executar o pg_dump no container e salvar o backup localmente
    dump_cmd = f"docker exec -t {CONTAINER_NAME} pg_dump -U {DB_USER} {DB_NAME} | gzip > {backup_file}"

    try:
        # Executa o comando de dump
        subprocess.run(dump_cmd, shell=True, check=True)
        print(f"Backup criado com sucesso: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar o backup: {e}")
        return None

# Função para enviar o backup para o Google Drive usando rclone
def upload_to_gdrive(backup_file):
    if backup_file and os.path.exists(backup_file):
        try:
            # Comando rclone para copiar o arquivo para o Google Drive
            rclone_cmd = f"rclone copy {backup_file} {RCLONE_REMOTE}"
            subprocess.run(rclone_cmd, shell=True, check=True)
            print(f"Backup enviado para o Google Drive com sucesso: {backup_file}")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao enviar o backup para o Google Drive: {e}")

# Função para remover backups antigos (ex: manter backups por 7 dias)
def cleanup_old_backups(days=7):
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    for filename in os.listdir(BACKUP_DIR):
        file_path = os.path.join(BACKUP_DIR, filename)
        if os.path.isfile(file_path):
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time < cutoff_date:
                os.remove(file_path)
                print(f"Backup antigo removido: {file_path}")

# Função principal para executar todo o processo
def main():
    # Criar o backup

    while True:
        
        backup_file = create_backup()

    # Enviar o backup para o Google Drive
        #upload_to_gdrive(backup_file)

    # Limpar backups antigos
        cleanup_old_backups(days=7)

        time.sleep(86400)
if __name__ == "__main__":
    main()
