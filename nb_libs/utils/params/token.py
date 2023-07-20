""" .token.jsonファイル操作クラス
"""

import os
import json
from http import HTTPStatus
from urllib import parse
import sys
from ..common import common
from ..gin import api
from ..message import display, message

def get_ginfork_token():
    """$HOME/.token.jsonからginfork_tokenを取得する。
    RETURN
    -----------------
    ginfork_token : str
        Description : token for gin-fork
    """
    os.chdir(os.environ['HOME'])
    file_path = '.token.json'
    with open(file_path, 'r') as f:
        data = json.load(f)
    ginfork_token = data['ginfork_token']
    return ginfork_token


def del_build_token_by_remote_origin_url(remote_origin_url, display_msg=True):
    """プライベートリポジトリ作成用トークンの削除

    ARG
    ---------------
    remote_origin_url : str
        Description : git config remote.origin.urlの値

    EXCEPTION
    ---------------
    requests.exceptions.RequestException :
        Description : 接続の確立不良。
        From : 下位モジュール

    """
    adjust_url, token = common.convert_url_remove_user_token(remote_origin_url)
    if len(token) > 0:
        # only private repo
        pr = parse.urlparse(adjust_url)
        response = api.delete_access_token(pr.scheme, pr.netloc, token=token)
        if response.status_code == HTTPStatus.OK:
            if display_msg:
                display.display_info(message.get("build_token", "success"))
        elif response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            if display_msg:
                display.display_info(message.get("build_token", "already_delete"))
        elif response.status_code == HTTPStatus.UNAUTHORIZED:
            if display_msg:
                display.display_info(message.get("build_token", "already_delete"))
        else:
            if display_msg:
                display.display_err(message.get("build_token", "error")+'Code[{}]'.format(response.status_code))
                raise Exception()
    else:
        pass
