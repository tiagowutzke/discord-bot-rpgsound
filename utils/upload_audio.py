import os
import boto3


def send_file_to_s3(filename, bucket, folder='audios'):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )

    file = f"./{folder}/{filename}" if folder is 'audios' else filename
    s3_file = filename.rsplit('/', 1)[-1]

    s3_params = {
        'ACL': 'public-read',
        'ContentType': 'audio/mpeg'
    } if folder is 'audios' else {}

    try:
        s3.upload_file(file, bucket, s3_file, ExtraArgs=s3_params)
        print("Upload Successful")
        return True
    except Exception as e:
        print(f"Error on send file to s3: {e}")
        return False


def is_valid_text(text):
    return text[-1] != ';'


def text_split_sentence_validation(text):
    while not is_valid_text(text):
        text = text[:-1]

    return text