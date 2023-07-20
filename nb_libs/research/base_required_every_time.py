import requests
import sys
sys.path.append('..')
from utils.message import message, display
from utils.params import token
from utils.gin import sync

def del_build_token():
    """不要なGIn-forkトークンの削除"""

    url = sync.get_remote_url()

    try:
        # delete build token(only private)
        token.del_build_token_by_remote_origin_url(url)
    except requests.exceptions.RequestException as e:
        display.display_err(message.get('communication', 'error'))
        raise e
    except Exception as e:
        raise e