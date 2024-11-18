from flask import Flask, render_template, request, send_file
import os
import shutil
from datetime import datetime
from zipfile import ZipFile

app = Flask(__name__)
BASE_PATH = "/path/to/your/photo/directory"  # Substitua pelo caminho real

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress_photos():
    try:
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        # Converter as datas para timestamps
        start_timestamp = datetime.strptime(start_date, '%Y-%m-%d').timestamp()
        end_timestamp = datetime.strptime(end_date, '%Y-%m-%d').timestamp()
        
        # Caminho para o ZIP temporário
        zip_path = os.path.join('compressed', 'photos.zip')
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        # Criar o ZIP
        with ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(BASE_PATH):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_timestamp = os.path.getmtime(file_path)

                    # Verifica se o arquivo está dentro do intervalo de datas
                    if start_timestamp <= file_timestamp <= end_timestamp:
                        arcname = os.path.relpath(file_path, BASE_PATH)
                        zipf.write(file_path, arcname)
        
        return send_file(zip_path, as_attachment=True)
    except Exception as e:
        return f"Erro: {str(e)}", 500

if __name__ == '__main__':
    os.makedirs('compressed', exist_ok=True)
    app.run(debug=True)
