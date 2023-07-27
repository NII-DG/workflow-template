""".sshを利用するメソッド群"""
import os
import requests
from http import HTTPStatus
from urllib import parse
from . import api
from ..params import token, param_json
from ..common import common
from ..message import message as msg_mod, display as msg_display
from ..path import path as p


SSH_PATH = os.path.join(p.HOME_PATH, ".ssh")
__SSH_KEY_PATH = os.path.join(SSH_PATH, "id_ed25519")
__SSH_PUB_KEY_PATH = os.path.join(SSH_PATH, "id_ed25519.pub")
__SSH_CONFIG = os.path.join(SSH_PATH, "config")


def create_key():
    """SSHキーを作成"""
    if not os.path.isfile(__SSH_KEY_PATH):
        common.exec_subprocess(f'ssh-keygen -t ed25519 -N "" -f {__SSH_KEY_PATH}')
        msg_display.display_info(msg_mod.get('setup', 'ssh_create_success'))
    else:
        msg_display.display_warm(msg_mod.get('setup', 'ssh_already_create'))


def upload_ssh_key():
    """GIN-forkへ公開鍵を登録"""

    try:
        with open(__SSH_PUB_KEY_PATH, mode='r') as f:
            ssh_key = f.read()

        params = param_json.get_params()
        pr = parse.urlparse(params['siblings']['ginHttp'])
        response = api.upload_key(pr.scheme, pr.netloc, token.get_ginfork_token(), ssh_key)
        msg = response.json()

        if response.status_code == HTTPStatus.CREATED:
            msg_display.display_info(msg_mod.get('setup', 'ssh_upload_success'))
        elif msg['message'] == 'Key content has been used as non-deploy key':
            msg_display.display_warm(msg_mod.get('setup', 'ssh_already_upload'))
        else:
            response.raise_for_status()

    except requests.exceptions.RequestException:
        msg_display.display_err(msg_mod.get('setup', 'connection_error'))
        raise
    except Exception:
        msg_display.display_err(msg_mod.get('setup', 'unexpected'))
        raise


def trust_gin():
    """SSHホスト（=GIN）を信頼する設定"""
    params = param_json.get_params()
    config_GIN(ginHttp=params['siblings']['ginHttp'])


def config_GIN(ginHttp):
    """リポジトリホスティングサーバのURLからドメイン名を抽出してコンテナに対してSHH通信を信頼させるメソッド
        この時、/home/jovyan/.ssh/configファイルに設定値を出力する。
    ARG
    ---------------------------
    ginHttp : str
        Description : リポジトリホスティングサーバのURL ex : http://dg01.dg.rcos.nii.ac.jp
    """
    # SSHホスト（＝GIN）を信頼する設定
    path = __SSH_CONFIG
    s = ''
    pr = parse.urlparse(ginHttp)
    ginDomain = pr.netloc
    if os.path.exists(path):
        with open(path, 'r') as f:
            s = f.read()
        if s.find('host ' + ginDomain + '\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile=/dev/null') == -1:
            # 設定が無い場合は追記する
            with open(path, mode='a') as f:
                write_GIN_config(mode='a', ginDomain=ginDomain)
        else:
            # すでにGINを信頼する設定があれば何もしない
            pass
    else:
        # 設定ファイルが無い場合は新規作成して設定を書きこむ
        with open(path, mode='w') as f:
            write_GIN_config(mode='w', ginDomain=ginDomain)


def write_GIN_config(mode, ginDomain):
    with open(__SSH_CONFIG, mode) as f:
        f.write('\nhost ' + ginDomain + '\n')
        f.write('\tStrictHostKeyChecking no\n')
        f.write('\tUserKnownHostsFile=/dev/null\n')










