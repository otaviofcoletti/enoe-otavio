import os
import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi

# Inicializa a API do Kaggle
api = KaggleApi()
api.authenticate()

# Caminhos das pastas de imagens
image_paths = ['images/2024/12', 'images/2025/01']

# Nome do dataset e descrição
dataset_name = 'my_image_dataset'
dataset_title = 'My Image Dataset'
dataset_description = 'Dataset containing images from December 2024 and January 2025.'

# Cria um diretório temporário para o dataset
os.makedirs(dataset_name, exist_ok=True)

# Copia as imagens para o diretório do dataset
for path in image_paths:
    for file_name in os.listdir(path):
        full_file_name = os.path.join(path, file_name)
        if os.path.isfile(full_file_name):
            os.system(f'cp {full_file_name} {dataset_name}/')

# Cria o arquivo metadata.json
metadata = {
    'title': dataset_title,
    'id': f'{api.username}/{dataset_name}',
    'licenses': [{'name': 'CC0-1.0'}]
}

with open(f'{dataset_name}/dataset-metadata.json', 'w') as f:
    json.dump(metadata, f, indent=4)

# Faz o upload do dataset para o Kaggle
api.dataset_create_new(dataset_name, dir_mode='zip')