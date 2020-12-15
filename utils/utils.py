import os
import boto3


def get_table_name(table):
    if table == 'music':
        return 'musica_ambiente'
    elif table == 'ambience':
        return 'som_ambiente'
    return 'efeito_sonoro'


def delete_file_from_s3(file):
    bucket = os.environ.get('S3_BUCKET')
    s3 = boto3.resource("s3")
    obj = s3.Object(bucket, file)
    obj.delete()


def get_file_from_s3(bucket, key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )
    response = s3.get_object(Bucket=bucket, Key=key)

    return response['Body'].read()


def run_bot(bot):
    os.system(f"python3 bots/{bot}.py")


def check_bot_run(audio_type, audio_url):
    if audio_type == 'efeito_sonoro':
        os.system('pkill -f sound_bot_speech')
        os.system(f'python3 ./bots/sound_bot_speech.py {audio_url}')
    elif audio_type == 'som_ambiente':
        os.system('pkill -f ambience_bot_speech')
        os.system(f'python3 ./bots/ambience_bot_speech.py {audio_url}')
    else:
        os.system('pkill -f music_bot_speech')
        os.system(f'python3 ./bots/music_bot_speech.py {audio_url}')


def beautify_response(response):
    result = response.replace('/', '').replace("'", '').replace('"', '')
    result = result.strip('][').strip(')(').split(', ')

    if len(result) == 1 and result[0] == '':
        return False

    return result


def make_list_from_suggestions(suggestions_list, step=3):
    result = []
    suggestions_size = len(suggestions_list)

    for i in range(0, suggestions_size, step):
        suggestion = []
        for j in range(step):
            suggestion.append(suggestions_list[i+j])
        result.append(suggestion)

    return result
