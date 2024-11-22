from flask import Flask, render_template, request, send_file, url_for
import os
from datetime import datetime, timedelta
from zipfile import ZipFile
from flask import redirect, url_for
import threading



app = Flask(__name__)
BASE_PATH = "/home/enoe/enoe-backup/images"  # Substitua pelo caminho real
COMPRESSED_PATH = "compressed"  # Diretório para salvar os zips gerados


def compress_photos(start_date, end_date):

    # Nome do arquivo ZIP com datas
    zip_name = f"photos_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_compressing.zip"
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
                    print(f"Compressing {photo}")
                    file_path = os.path.join(day_path, photo)
                    arcname = os.path.relpath(file_path, BASE_PATH)
                    zipf.write(file_path, arcname)
            
            current_date += timedelta(days=1)  # Incrementa para o próximo dia
    # Renomear o arquivo ZIP para remover o sufixo "_compressing"
    final_zip_name = zip_name.replace("_compressing", "")
    final_zip_path = os.path.join(COMPRESSED_PATH, final_zip_name)
    os.rename(zip_path, final_zip_path)
    
@app.route('/')
def index():
    # Listar os arquivos ZIP gerados
    files = os.listdir(COMPRESSED_PATH)
    files = [{"name": file, "url": url_for('download', filename=file)} for file in files]
    return render_template('index.html', files=files)
    

@app.route('/compress', methods=['POST'])
def compress():
    try:
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        # Converter as datas para datetime
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        thread = threading.Thread(target=compress_photos, args=(start_date, end_date))
        thread.start()
        
        
        return redirect(url_for('processing'))
    except Exception as e:
        return f"Erro: {str(e)}", 500

@app.route('/processing')
def processing():
    return render_template('processing.html')

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(COMPRESSED_PATH, filename), as_attachment=True)

if __name__ == '__main__':
    os.makedirs(COMPRESSED_PATH, exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
