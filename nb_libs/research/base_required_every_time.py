import requests
from ..utils.message import message, display
from ..utils.params import token
from ..utils.git import git_module

def del_build_token():
    """不要なGIN-forkトークンの削除"""

    url = git_module.get_remote_url()

    try:
        # delete build token(only private)
        token.del_build_token_by_remote_origin_url(url)
    except requests.exceptions.RequestException as e:
        display.display_err(message.get('build_token', 'communication_error'))
        raise e
    except Exception as e:
        raise e