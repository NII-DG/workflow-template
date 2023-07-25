""" .user_infoファイル操作クラス
"""

import os
import json
import requests
from ..path import path as p
from . import param_json


file_path = os.path.join(p.SYS_PATH, '.user_info.json')


def get_user_id():
    """$HOME/.user_infoからユーザーIDを取得する。
    RETURN
    -----------------
    user_id : str
        Description : ユーザーID
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    user_id = data['user_id']
    return user_id


def set_user_info(name):
    """
    ユーザー情報を.user_info.jsonに登録する。

    Parameters
    ---------------
    name : str
        Description : ユーザー名
    """

    # APIリクエストに必要な情報を取得する
    params = param_json.get_params()

    # ユーザー名からuidを取得する
    baseURL = params['siblings']['ginHttp'] + '/api/v1/users/'
    response = requests.get(baseURL + name)
    uid = response.json()['id']

    user_info = {"user_id":uid}
    with open(file_path, 'w') as f:
        json.dump(user_info, f, indent=4)