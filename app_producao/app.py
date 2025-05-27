from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from datetime import datetime

import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
import psycopg2
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)

IMAGE_FOLDER = os.environ['IMAGE_FOLDER']

db_config = {
    'dbname':   os.environ['DB_NAME'],
    'user':     os.environ['DB_USER'],
    'password': os.environ['DB_PASSWORD'],
    'host':     os.environ['DB_HOST'],
    'port':     os.environ['DB_PORT'],
}


def get_all_images():
    images = []
    for root, dirs, files in os.walk(IMAGE_FOLDER):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # Caminho completo do arquivo
                filepath = os.path.join(root, filename)

                # Extraindo o caminho relativo e separando ano/mês/dia
                relative_path = os.path.relpath(filepath, IMAGE_FOLDER).replace('\\', '/')
                path_parts = relative_path.split('/')

                # Extraindo a data do caminho (ano, mês, dia)
                year, month, day = path_parts[-4], path_parts[-3], path_parts[-2]

                # A data já está no nome do arquivo e já deve estar no formato com dois dígitos
                date = f"{year}-{month}-{day}"

                # Adicionando as informações à lista
                images.append({
                    'filename': filename,
                    'date': date,
                    'relative_path': relative_path
                })

    # Ordenar as imagens pela data mais recente, com base na data no nome do arquivo
    images.sort(key=lambda x: x['relative_path'], reverse=True)
    return images

@app.route('/publications')
def publications():
    return render_template('publications.html')


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/last_photo')
def last_photo():
    images = get_all_images()
    if not images:
        return "Nenhuma imagem encontrada."
    index = int(request.args.get('index', 0))
    if index < 0:
        index = 0
    elif index >= len(images):
        index = len(images) - 1
    image = images[index]
    return render_template('last_photo.html', image=image, index=index, total=len(images))

@app.route('/select_day', methods=['GET', 'POST'])
def select_day():
    if request.method == 'POST':
        selected_date = request.form.get('date')
        return redirect(url_for('photos_on_day', date=selected_date))
    dates = sorted({img['date'] for img in get_all_images()}, reverse=True)
    return render_template('select_day.html', dates=dates)

@app.route('/photos_on_day', methods=['GET', 'POST'])
def photos_on_day():
    date = request.args.get('date')
    images = [img for img in get_all_images() if img['date'] == date]
    if not images:
        return "Nenhuma imagem encontrada para esta data."

    # Obter o índice da imagem atual
    index = request.args.get('index', 0)
    try:
        index = int(index)
    except ValueError:
        index = 0

    if index < 0:
        index = 0
    elif index >= len(images):
        index = len(images) - 1

    image = images[index]

    return render_template('photos_on_day.html', images=images, image=image, index=index, total=len(images), date=date)

# Rota para servir imagens do diretório de imagens
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

# Add enumerate to Jinja2 environment
app.jinja_env.globals.update(enumerate=enumerate)




def get_data(day, interval):
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    # Ajustando o timestamp para GMT-3 no SQL
    cur.execute("""
        SELECT to_char(to_timestamp(epoch::bigint) AT TIME ZONE 'America/Sao_Paulo', 'YYYY-MM-DD HH24:MI:SS') AS timestamp_local,
               distance_mm
        FROM ultrasonic
        WHERE to_char(to_timestamp(epoch::bigint) AT TIME ZONE 'America/Sao_Paulo', 'YYYY-MM-DD') = %s
        ORDER BY epoch;
    """, (day,))
    data = cur.fetchall()
    cur.close()
    conn.close()

    # Filtrar dados com base no intervalo em minutos
    filtered_data = []
    last_time = None
    for timestamp_local, value in data:
        current_time = datetime.strptime(timestamp_local, '%Y-%m-%d %H:%M:%S')
        if last_time is None or (current_time - last_time).total_seconds() >= interval * 60:
            filtered_data.append((timestamp_local, value))
            last_time = current_time

    return filtered_data

@app.route('/ultrasonic', methods=['GET', 'POST'])
def ultrasonic():
    # Obtém o dia atual no horário de São Paulo
    day = request.form.get('day', (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d'))
    interval = int(request.form.get('interval', 1))
    data = get_data(day, interval)
    
    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    
    return render_template('ultrasonic.html', data=data, day=day, labels=labels, values=values)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2021)
