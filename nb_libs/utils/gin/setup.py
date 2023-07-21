"""ローカルの初期セットアップ用"""
import os
import json
import requests
from http import HTTPStatus
import subprocess
from urllib import parse
from . import api
from ..gin import sync
from ..params import token
from ..message import message, display


__SSH_KEY_PATH = os.path.join(os.environ['HOME'], ".ssh/id_ed25519")


def datalad(path:str):
    """dataladのデータセット化する

    Args:
        path (str): データセット化するディレクトリのパス
    """
    if os.path.isdir(os.path.join(path, ".datalad")):
        subprocess.getoutput('datalad create --force ' + path)


def ssh_key():
    """SSHキーを作成"""
    if os.path.isfile(__SSH_KEY_PATH):
        subprocess.getoutput('ssh-keygen -t ed25519 -N "" -f ' + __SSH_KEY_PATH)


def upload_ssh_key():
    """GIN-forkへ公開鍵を登録"""

    try:
        with open(__SSH_KEY_PATH, mode='r') as f:
            ssh_key = f.read()

        with open(sync.fetch_param_file_path(), mode='r') as f:
            params = json.load(f)

        pr = parse.urlparse(params['siblings']['ginHttp'])
        response = api.upload_key(pr.scheme, pr.netloc, token.get_ginfork_token(), ssh_key)
        msg = response.json()

        if response.status_code == HTTPStatus.CREATED:
            display.display_info(message.get('ssh_key', 'success'))
        elif msg['message'] == 'Key content has been used as non-deploy key':
            display.display_warm(message.get('ssh_key', 'already_exist'))
        else:
            raise Exception

    except requests.exceptions.RequestException as e:
        display.display_err(message.get('ssh_key', 'communication_error'))
        raise e
    except Exception as e:
        display.display_err(message.get('ssh_key', 'unexpected'))
        raise e




