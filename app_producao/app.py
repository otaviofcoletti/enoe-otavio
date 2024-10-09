from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from datetime import datetime

app = Flask(__name__)

# Defina o caminho para a pasta que contém as imagens
IMAGE_FOLDER = '/home/intermidia/enoe-otavio/Server/images'

def get_all_images():
    images = []
    for root, dirs, files in os.walk(IMAGE_FOLDER):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                filepath = os.path.join(root, filename)
                mod_time = os.path.getmtime(filepath)
                date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d')
                relative_path = os.path.relpath(filepath, IMAGE_FOLDER)
                images.append({
                    'filename': filename,
                    'mod_time': mod_time,
                    'date': date,
                    'relative_path': relative_path.replace('\\', '/')
                })
    images.sort(key=lambda x: x['mod_time'], reverse=True)
    return images

@app.route('/')
def index():
    images = get_all_images()
    if not images:
        return "Nenhuma imagem encontrada."
    index = int(request.args.get('index', 0))
    if index < 0:
        index = 0
    elif index >= len(images):
        index = len(images) - 1
    image = images[index]
    return render_template('index.html', image=image, index=index, total=len(images))

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
