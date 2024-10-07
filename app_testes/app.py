from flask import Flask, render_template, send_from_directory, request
import os

app = Flask(__name__)

# Defina o caminho base das imagens
IMAGE_FOLDER = '/home/intermidia/enoe-otavio/Server/images/2024/9'

@app.route('/')
def index():
    # Obtenha o último dia de imagens
    last_date = max(os.listdir(IMAGE_FOLDER))
    images = sorted(os.listdir(os.path.join(IMAGE_FOLDER, last_date)))

    return render_template('index.html', images=images, current_image=images[-1], date=last_date)

@app.route('/image/<path:filename>')
def get_image(filename):
    # Servir as imagens da pasta correta
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/select-day', methods=['POST'])
def select_day():
    # Carregar imagens do dia selecionado
    selected_date = request.form.get('date')
    images = sorted(os.listdir(os.path.join(IMAGE_FOLDER, selected_date)))

    return render_template('index.html', images=images, current_image=images[0], date=selected_date)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
