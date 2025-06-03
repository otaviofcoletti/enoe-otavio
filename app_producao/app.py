import os
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import psycopg2

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


#
# === CACHE somente para get_all_images_for_date ===
#
# Mantemos um dicionário global: cache_por_data = { 'YYYY-MM-DD': (timestamp_em_epoch, [lista_de_imagens]) }
# Expiramos o cache de cada data após CACHE_TIMEOUT segundos.
#
CACHE_TIMEOUT = 60  # em segundos, ajuste conforme necessidade

cache_por_data = {}  # formato: { date_str: (timestamp, images_list) }


def get_all_images_for_date(date):
    """
    Retorna lista de {'filename', 'date', 'relative_path'} para a pasta /YYYY/MM/DD/.
    Usa cache: se a data estiver em cache e não expirou, retorna direto.
    Caso contrário, faz os os.walk e atualiza o cache.
    """
    now = time.time()

    # Verifica no cache
    if date in cache_por_data:
        timestamp, imagens = cache_por_data[date]
        if now - timestamp < CACHE_TIMEOUT:
            # Cache ainda válido
            return imagens

    # Se chegou aqui, cache não existe ou expirou → recarrega do disco
    year, month, day = date.split('-')
    folder_path = os.path.join(IMAGE_FOLDER, year, month, day)

    imagens = []
    if os.path.isdir(folder_path):
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    filepath = os.path.join(root, filename)
                    rel_path = os.path.relpath(filepath, IMAGE_FOLDER).replace('\\', '/')
                    imagens.append({
                        'filename': filename,
                        'date': date,
                        'relative_path': rel_path
                    })
        # Ordena do mais recente para o mais antigo (por nome de arquivo, na mesma data)
        imagens.sort(key=lambda x: x['relative_path'], reverse=True)

    # Atualiza o cache
    cache_por_data[date] = (now, imagens)
    return imagens


#
# === Rotas do Flask ===
#

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/publications')
def publications():
    return render_template('publications.html')


@app.route('/select_day', methods=['GET', 'POST'])
def select_day():
    """
    Lista todas as datas que têm imagens (sem cache, pois não é tão pesado).
    Em POST, redireciona para /photos_on_day?date=...
    """
    if request.method == 'POST':
        selected_date = request.form.get('date')
        return redirect(url_for('photos_on_day', date=selected_date))

    # Descobre todas as pastas YYYY/MM/DD que contêm pelo menos 1 arquivo de imagem
    dates = set()
    for root, dirs, files in os.walk(IMAGE_FOLDER):
        if any(f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) for f in files):
            rel_path = os.path.relpath(root, IMAGE_FOLDER).replace('\\', '/')
            parts = rel_path.split('/')
            if len(parts) >= 3:
                year, month, day = parts[-3], parts[-2], parts[-1]
                date_str = f"{year}-{month}-{day}"
                try:
                    datetime.strptime(date_str, "%Y-%m-%d")
                    dates.add(date_str)
                except ValueError:
                    pass

    dates = sorted(dates, reverse=True)
    return render_template('select_day.html', dates=dates)


@app.route('/photos_on_day')
def photos_on_day():
    """
    Exibe as fotos de uma data específica (via ?date=YYYY-MM-DD).
    Navegação por índice usando 'index' na query string.
    """
    date = request.args.get('date')
    if not date:
        return redirect(url_for('select_day'))

    imagens = get_all_images_for_date(date)
    if not imagens:
        return render_template('no_image.html', msg="Nenhuma imagem para essa data."), 404

    # Obtém índice de navegação (prev/next)
    try:
        index = int(request.args.get('index', 0))
    except ValueError:
        index = 0

    index = max(0, min(index, len(imagens) - 1))
    imagem = imagens[index]

    return render_template('photos_on_day.html',
                           images=imagens,
                           image=imagem,
                           index=index,
                           total=len(imagens),
                           date=date)


@app.route('/last_photo')
def last_photo():
    """
    Exibe a foto mais recente de TODAS as datas disponíveis.
    Aqui não fazemos cache de TODAS as imagens; para obter a mais recente:
     1) listamos todas as datas disponíveis (igual ao select_day)
     2) ordenamos as datas decrescentemente
     3) para cada data (da mais nova para a mais antiga), chamamos get_all_images_for_date(date)
        e, se encontrar pelo menos 1 imagem, retornamos a primeira (já ordenada internamente).
    Assim evitamos varrer toda a árvore de uma vez, parando na primeira data que tenha imagens.
    """
    # 1) Descobre todas as datas (mesma lógica do select_day)
    dates = set()
    for root, dirs, files in os.walk(IMAGE_FOLDER):
        if any(f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) for f in files):
            rel_path = os.path.relpath(root, IMAGE_FOLDER).replace('\\', '/')
            parts = rel_path.split('/')
            if len(parts) >= 3:
                year, month, day = parts[-3], parts[-2], parts[-1]
                date_str = f"{year}-{month}-{day}"
                try:
                    datetime.strptime(date_str, "%Y-%m-%d")
                    dates.add(date_str)
                except ValueError:
                    pass

    sorted_dates = sorted(dates, reverse=True)

    # 2) Itera sobre datas da mais nova para a mais antiga, buscando o primeiro set de imagens
    for dt in sorted_dates:
        imagens = get_all_images_for_date(dt)
        if imagens:
            # achamos imagens para esta data; pegamos a primeira (mais recente desta data)
            # Se quiser navegar por “todas as imagens” (de todas as datas concatenadas),
            # seria necessário acumular listas; mas aqui só exibimos a mais recente.
            imagem = imagens[0]
            return render_template('last_photo.html',
                                   image=imagem,
                                   index=0,
                                   total=1)  # total=1, pois só mostramos a primeira

    # Se chegou aqui, não encontrou nenhuma imagem em toda a árvore
    return render_template('no_image.html', msg="Nenhuma imagem encontrada."), 404


# Rota (em dev) para servir imagens. Em produção, remova esta rota
# e deixe que o Nginx/Apache sirva IMAGE_FOLDER diretamente.
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)


# Permite usar enumerate() nos templates Jinja2
app.jinja_env.globals.update(enumerate=enumerate)


def get_data(day, interval):
    """
    Consulta os dados do sensor ultrassônico no PostgreSQL, filtra por intervalo e retorna lista de tuples.
    """
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""
        SELECT to_char(
                 to_timestamp(epoch::bigint) AT TIME ZONE 'America/Sao_Paulo',
                 'YYYY-MM-DD HH24:MI:SS'
               ) AS timestamp_local,
               distance_mm
        FROM ultrasonic
        WHERE to_char(
                to_timestamp(epoch::bigint) AT TIME ZONE 'America/Sao_Paulo',
                'YYYY-MM-DD'
              ) = %s
        ORDER BY epoch;
    """, (day,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    filtered = []
    last_time = None
    for timestamp_local, value in rows:
        current_time = datetime.strptime(timestamp_local, '%Y-%m-%d %H:%M:%S')
        if last_time is None or (current_time - last_time).total_seconds() >= interval * 60:
            filtered.append((timestamp_local, value))
            last_time = current_time

    return filtered


@app.route('/ultrasonic', methods=['GET', 'POST'])
def ultrasonic():
    day = request.form.get('day',
                          (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d'))
    interval = request.form.get('interval', 1, type=int)
    data = get_data(day, interval)
    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    return render_template('ultrasonic.html',
                           data=data,
                           day=day,
                           labels=labels,
                           values=values)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2021, debug=True)
