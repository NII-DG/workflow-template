import requests
import nb_libs.utils.message.message as mess

def access_s3_url(url) -> str:
    """S3オブジェクトURLの検証を行う

    Return:
        エラーメッセージ

    """
    msg = ""
    try:
        response = requests.head(url)
        if response.status_code == 200:
            pass
        elif response.status_code == 404 or response.status_code == 400:
            msg = mess.get('from_s3', 'wrong_url')
        elif response.status_code == 403:
            msg = mess.get('from_s3', 'private_object')
        else:
            msg = mess.get('from_s3', 'exception')
    except requests.exceptions.RequestException:
        msg = mess.get('from_s3', 'wrong_url')
    return msg