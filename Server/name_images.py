import os
import re

# Caminho base onde estão os arquivos de imagem
IMAGE_FOLDER = '/home/intermidia/enoe-otavio/Server/images'

def rename_images():
    for root, dirs, files in os.walk(IMAGE_FOLDER):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # Verifica se o nome do arquivo está no formato antigo (dia-mês-ano)
                match = re.match(r'(\d{2})-(\d{2})-(\d{4})_(\d{2}:\d{2}:\d{2})', filename)
                if match:
                    # Extraindo a data e hora do nome do arquivo
                    day, month, year, time = match.groups()
                    
                    # Novo nome no formato ano-mês-dia
                    new_filename = f"{year}-{month}-{day}_{time}{os.path.splitext(filename)[1]}"
                    
                    # Caminhos completo antigo e novo
                    old_filepath = os.path.join(root, filename)
                    new_filepath = os.path.join(root, new_filename)
                    
                    # Renomeando o arquivo
                    os.rename(old_filepath, new_filepath)
                    print(f"Renamed: {old_filepath} -> {new_filepath}")

# Chama a função para renomear os arquivos
rename_images()
