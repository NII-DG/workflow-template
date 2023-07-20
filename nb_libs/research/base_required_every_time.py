import requests
import os
os.chdir(os.environ['HOME'], 'WORKFLOWS', 'nb_libs', 'utils')
from message import message, display
from params import token
from git import git_module

def del_build_token():
    """不要なGIN-forkトークンの削除"""

    url = git_module.get_remote_url()

    try:
        # delete build token(only private)
        token.del_build_token_by_remote_origin_url(url)
    except requests.exceptions.RequestException as e:
        display.display_err(message.get('communication', 'error'))
        raise e
    except Exception as e:
        raise e