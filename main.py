import os
import requests
import functools

from app import app
from werkzeug.utils import secure_filename
from flask import flash, request, redirect, render_template, url_for

from multiprocessing.pool import ThreadPool

from utils.load_suggestions import get_suggestion_by_id, update_suggestion, delete_suggestion
from utils.upload_audio import send_file_to_s3, text_split_sentence_validation
from database.adapter import get_database_objects

from utils.utils import (
    get_table_name, run_bot, delete_file_from_s3, beautify_response, make_list_from_suggestions, check_bot_run
)

ALLOWED_EXTENSIONS = set(['mp3', 'wav', 'webm', 'ogg'])

# Routes
index = '/'
index = '/'
upload = '/upload'
play = '/jogar'
play_discord = '/discord-bots'

audios = '/audios'
update_audio = '/update_audio'
delete_audio_route = '/delete_audio'
config = '/config'
search_audios = '/search_audios'
download_client = '/download-client'
train = '/train'

# Routes - bots api
get_discord_audio = '/get_discord_audio'
start_bots_routes = '/start_bots'
stop_bots_route = '/stop_bots'

# Routes - nlp
train_model = '/train_model'
train_model_lambda = '/train_model_lambda'
load_suggestions = '/load_suggestions'
save_suggestions = '/save_suggestions'
delete_suggestions = '/delete_suggestions'
classify_sentence = '/classify'
get_audio_by_label = '/audio_by_label'


# Bots
@app.route(start_bots_routes)
def start_bots():
    bots = ['sound_bot', 'ambience_bot', 'music_bot']

    pool = ThreadPool(processes=len(bots))
    pool.map_async(functools.partial(run_bot), (bot for bot in bots))
    pool.close()

    return 'Success'


@app.route(get_discord_audio)
def get_discord_audio_function():
    audio_url = request.args.get('audio_url')
    audio_type = request.args.get('audio_type')

    pool = ThreadPool(processes=1)
    pool.map_async(functools.partial(check_bot_run, audio_url=audio_url), [type for type in [audio_type]])
    pool.close()

    return 'Playing music in discord!'


@app.route(stop_bots_route)
def stop_bots_function():
    os.system('pkill -f bots')
    return 'Bots stoped!'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Pages
@app.route(index)
def index():
    return render_template(
        'index.html',
        title='RPG BOT SOUND',
        route=upload,
        route_play=play,
        route_play_discord=play_discord,
        route_audios=audios,
        route_config=config,
        route_train=train
    )


@app.route(play)
def play_page():
    return render_template('play.html', title='JOGANDO')


@app.route(play_discord)
def play_page_discord():
    stop_bots_function()
    return render_template('play_discord.html', title='BOTS DISCORD', bot_on=False)


@app.route(train)
def train_page():
    conn, persistance, query = get_database_objects()
    status, message, train_date = query.query_all(
        table='train_status',
        column="status, message, to_char(created_at - interval '3 hour', 'DD/MM/YYYY HH24:MI:SS')",
        use_where=False
    )[0]
    persistance.update_timed_out_train_status()
    conn.close()

    return render_template(
        'train.html',
        title='TREINAR BOT',
        status=status,
        message=message,
        train_date=train_date
    )


@app.route(train_model)
def train_model():
    conn, persistence, _ = get_database_objects()
    persistence.update_by_col(
        table='train_status',
        column='status',
        value='WAITING',
        where_col=1,
        col_value=1
    )
    conn.close()

    return train_page()


@app.route(train_model_lambda)
def train_model_lambda():
    lambda_url = os.environ.get('train_lambda_url')
    r = requests.get(lambda_url)
    return r.status_code


@app.route(save_suggestions)
def save_suggestions_function():
    suggestions = request.args.get('suggestions')
    audio_type = request.args.get('audio_type')

    conn, persistence, _ = get_database_objects()
    import ast

    suggestions = ast.literal_eval(suggestions)

    for suggestion in list(suggestions):

        label, score, validation = suggestion

        persistence.insert(
            table='label_suggestions',
            suggested_label=f"'{label}'",
            suggested_table=f"'{audio_type}'",
            score=score,
            validation=f"'{validation}'"
        )

    conn.close()

    return 'Suggestions saved!'


@app.route(load_suggestions)
def get_load_suggestions():
    conn, persistence, query = get_database_objects()

    transaction = request.args.get('transaction')
    id = request.args.get('id')

    if transaction == 'search':

        score = request.args.get('score')

        try:
            suggestions = query.query_all(
                table='label_suggestions',
                column='id, validation, suggested_label, suggested_table, round(score, 2)',
                where_col='score',
                where_type='bigger_than',
                value=score
            )
        except:
            conn.close()
            return False

        conn.close()

        return render_template('suggestions_tbody.html', suggestions=suggestions)

    elif transaction == 'update':
        table, label, validation = get_suggestion_by_id(query, id)
        update_successfull = update_suggestion(persistence, table, label, validation)

        if not update_successfull:
            flash('Algo errado aconteceu ao atualizar a sugestão. Tente novamente em alguns minutos...')
        else:
            delete_suggestion(persistence, id)

    elif transaction == 'delete':
        # Insert in not labels table
        table, label, validation = get_suggestion_by_id(query, id)
        persistence.insert(
            table=f'not_{table}',
            validation=f"'{validation}'",
            tag=f"'{label}'"
        )

        delete_suggestion(persistence, id)

    else:
        pass

    suggestions = query.query_all(
        table='label_suggestions',
        column='id, validation, suggested_label, suggested_table, round(score, 2)',
        use_where=False
    )
    conn.close()

    return render_template('suggestions_tbody.html', suggestions=suggestions)


@app.route(delete_suggestions)
def delete_suggestions_function():
    conn, persistence, _ = get_database_objects()
    persistence.delete_all('label_suggestions')
    conn.close()

    return ''


@app.route(classify_sentence)
def classify_sentence_function():
    lambda_url = os.environ.get('classify_lambda_url')

    sentence = request.args.get('sentence')
    type = request.args.get('type')

    data = {"sentence": sentence, "type": type}

    r = requests.get(lambda_url, params=data)
    response = beautify_response(r.text)

    if not response:
        return '{}'

    print(response)

    try:
        label = response[0]
        score = response[1]
        suggestions = beautify_response(str(response[2:]))

        suggestions = make_list_from_suggestions(list(suggestions)) if suggestions else ''
    except:
        return f'{{Error: {response}}}'

    return f'{{"label": "{label}", "score": "{score}", "suggestions":"{suggestions}"}}'


@app.route(get_audio_by_label)
def get_audio_by_label_function():
    type = request.args.get('type')
    label = request.args.get('label')

    conn, _, query = get_database_objects()

    try:
        filename = query.query_all(
            table=type,
            column='filename',
            where_col='tag',
            value=label
        )
        import random

        return random.choice(filename)[0]
    except:
        return ''


@app.route(audios)
def audios_list():
    conn, persistance, query = get_database_objects()

    s3_url = 'https://audios-rpg-sound.s3-us-west-1.amazonaws.com'
    columns = f"id, tag, validation, filename, replace(filename, '{s3_url}', '')"

    music_audios = query.query_all(table='musica_ambiente', column=columns, use_where=False) if not False else ''
    sound_audios = query.query_all(table='efeito_sonoro', column=columns, use_where=False) if not False else ''
    ambience_audios = query.query_all(table='som_ambiente', column=columns, use_where=False) if not False else ''

    audios_query = [music_audios, sound_audios, ambience_audios]
    titles = ['_', 'Músicas', 'Efeitos sonoros', 'Som ambiente']
    titles_ids = ['_', 'music', 'sound', 'ambience']

    conn.close()

    return render_template(
        'audios.html',
        title='LISTA DE ÁUDIOS',
        audios=audios_query,
        titles=titles,
        titles_ids=titles_ids,
        route_update_audio=update_audio,
        route_delete_audio=delete_audio_route
    )


# Delete audio in database and S3
@app.route(delete_audio_route, methods=['GET', 'POST'])
def delete_audio():
    if request.method == 'POST':
        id = request.form['id']
        table = request.form['table']

        file = request.form['file'].rsplit('/', 1)[-1]
        delete_file_from_s3(file)

        table = get_table_name(table)

        conn, persistence, _ = get_database_objects()
        persistence.delete_by_id(table, id)
        conn.close()

    return redirect(url_for('audios_list'))


# Update audio in database
@app.route(update_audio, methods=['GET', 'POST'])
def update_audio_database():
    if request.method == 'POST':

        conn, persistence, _ = get_database_objects()

        id = request.form['id']
        column = request.form['column']
        table = request.form['table']
        update_all_tags = True if request.form.get('all-tags') == 'on' else False

        validation = request.form.get('validation')
        tag = request.form.get('tag')

        if validation:
            value = validation
            value = text_split_sentence_validation(value)
        else:
            value = tag

        table = get_table_name(table)

        if update_all_tags:
            persistence.update_by_col(table, column, value, where_col='tag', col_value=f"'{tag}'")
        else:
            persistence.update_by_col(table, column, value, where_col='id', col_value=id)

        conn.close()

    return redirect(url_for('audios_list'))


# Upload audio
@app.route(upload)
def upload_form():
    return render_template('upload.html', title='ENVIAR ARQUIVO DE ÁUDIO', submit_route=upload)


@app.route(upload, methods=['POST'])
def upload_file():
    conn, persistance, query = get_database_objects()

    # Getting html form values
    option = request.form['option']
    validation = request.form['validacao']
    tag = request.form['tag']

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash(f'Allowed file types are {ALLOWED_EXTENSIONS}')
            return redirect(request.url)

        result = persistance.insert(
            table=option,
            tag=f"'{tag}'",
            validation=f"'{validation}'",
            filename=f"'https://audios-rpg-sound.s3-us-west-1.amazonaws.com/{filename}'"
        )

        conn.close()

        if result:
            bucket = os.environ.get('S3_BUCKET')
            send_file_to_s3(filename, bucket)
            flash("Enviado com sucesso!")
        else:
            flash("Algo deu errado..")

        return redirect(request.url)


@app.route(config)
def open_config():
    conn, _, query = get_database_objects()

    voice_id, text_id, score_single, score_multiple, score_suggestion = query.query_config()
    conn.close()

    return render_template(
        'config.html',
        title='CONFIGURAÇÕES',
        submit_route=config,
        voice_id=voice_id,
        text_id=text_id,
        score_single=score_single,
        score_multiple=score_multiple,
        score_suggestion=score_suggestion
    )


@app.route(config, methods=['POST'])
def save_config():
    if request.method == 'POST':
        conn, persistance, _ = get_database_objects()

        # Getting html form values
        text_id = request.form['text_id']
        voice_id = request.form['voice_id']
        score_single = request.form['score_single']
        score_multiple = request.form['score_multiple']
        score_suggestions = request.form['score_suggestion']

        success = persistance.update_config(
            channel_text_id=f"'{text_id}'",
            channel_voice_id=f"'{voice_id}'",
            valid_score_single_pred=f"'{score_single}'",
            valid_score_multiple_pred=f"'{score_multiple}'",
            valid_score_suggestions=f"'{score_suggestions}'"
        )

        if not success:
            flash('Algo errado aconteceu...')
        else:
            flash('Configurações salvas!')

        conn.close()

    return redirect(request.url)


@app.route(search_audios)
def get_search_audios():
    search = request.args.get('search_text')
    column = request.args.get('column')
    table = request.args.get('table')

    if table == 'music':
        table = 'musica_ambiente'
    elif table == 'ambience':
        table = 'som_ambiente'
    else:
        table = 'efeito_sonoro'

    conn, _, query = get_database_objects()

    s3_url = 'https://audios-rpg-sound.s3-us-west-1.amazonaws.com'
    columns = f"id, tag, validation, filename, replace(filename, '{s3_url}', '')"

    audios_query = query.query_all(table=table, column=columns, where_col=column, value=search) if not False else ''
    conn.close()

    return render_template(
        'table_body.html',
        audio=audios_query,
        table=table,
        route_update_audio=update_audio,
        route_delete_audio=delete_audio_route
    )


if __name__ == "__main__":
    port = int(os.environ.get('PORT', os.environ['PORT']))
    app.run(host='0.0.0.0', port=port, debug=True)

