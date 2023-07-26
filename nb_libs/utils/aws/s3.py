import requests
from ..message import message

def access_s3_url(url:str) -> str:
    """S3オブジェクトURLの検証を行う
    Args:
        url(str): S3オブジェクトのURL

    Return:
        str: エラーメッセージ

    """
    msg = ""
    try:
        response = requests.head(url)
        if response.status_code == 200:
            pass
        elif response.status_code in [301, 403, 404]:
            msg = message.get('from_repo_s3', 'wrong_or_private')
        else:
            msg = message.get('from_repo_s3', 'unexpected')
    except requests.exceptions.RequestException:
        msg = message.get('from_repo_s3', 'wrong_or_private')
    return msg
    