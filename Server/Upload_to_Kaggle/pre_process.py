import pandas as pd
import datetime

# Caminho para o arquivo CSV
csv_file_path = '/home/intermidia/enoe-otavio/Server/Upload_to_Kaggle/ultrasonic.csv'

# Ler o arquivo CSV
df = pd.read_csv(csv_file_path)

# Procurar pela data mais próxima na coluna 'epoch'
date_to_find = '2024-12-07'
target_epoch = int(datetime.datetime.strptime(date_to_find, '%Y-%m-%d').timestamp())

# Converter a coluna 'epoch' para int
df['epoch'] = pd.to_numeric(df['epoch'], errors='coerce').fillna(0).astype(int)

# Encontrar a linha com a data mais próxima
filtered_df = df.iloc[(df['epoch'] - target_epoch).abs().argsort()[:1]]

# Exibir o resultado
print(filtered_df)

# Filtrar os dados que vêm após a epoch 1733529598
epoch_threshold = 1733529598
filtered_df = df[df['epoch'] > epoch_threshold]

# Salvar o novo DataFrame em um novo arquivo CSV
new_csv_file_path = '/home/intermidia/enoe-otavio/Server/Upload_to_Kaggle/ultrasonic_filtered.csv'
filtered_df.to_csv(new_csv_file_path, index=False)

# Repetir o processo para os outros arquivos CSV
for file_name in ['raspberry.csv', 'weather.csv']:
    csv_file_path = f'/home/intermidia/enoe-otavio/Server/Upload_to_Kaggle/{file_name}'
    df = pd.read_csv(csv_file_path)
    df['epoch'] = pd.to_numeric(df['epoch'], errors='coerce').fillna(0).astype(int)
    filtered_df = df[df['epoch'] > epoch_threshold]
    new_csv_file_path = f'/home/intermidia/enoe-otavio/Server/Upload_to_Kaggle/{file_name.split(".")[0]}_filtered.csv'
    filtered_df.to_csv(new_csv_file_path, index=False)