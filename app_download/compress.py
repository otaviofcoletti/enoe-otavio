from flask import Flask, render_template, request, send_file, url_for
import os
from datetime import datetime, timedelta
from zipfile import ZipFile
from flask import redirect, url_for

#YYYY-MM-DD

BASE_PATH = "/home/enoe/enoe-backup/images"  # Substitua pelo caminho real
COMPRESSED_PATH = "compressed"  # Diretório para salvar os zips gerados        
        
start_date = "2024-11-01"
end_date = "2024-11-02"

# Converter as datas para datetime
start_date = datetime.strptime(start_date, '%Y-%m-%d')
end_date = datetime.strptime(end_date, '%Y-%m-%d')

# Nome do arquivo ZIP com datas
zip_name = f"photos_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.zip"
zip_path = os.path.join(COMPRESSED_PATH, zip_name)

# Criar o ZIP
with ZipFile(zip_path, 'w') as zipf:
    current_date = start_date
    while current_date <= end_date:
        year = current_date.strftime('%Y')
        month = current_date.strftime('%m')
        day = current_date.strftime('%d')

        day_path = os.path.join(BASE_PATH, year, month, day)
        
        if os.path.exists(day_path):
            for photo in os.listdir(day_path):
                file_path = os.path.join(day_path, photo)
                arcname = os.path.relpath(file_path, BASE_PATH)
                zipf.write(file_path, arcname)
        
        current_date += timedelta(days=1)  # Incrementa para o próximo dia