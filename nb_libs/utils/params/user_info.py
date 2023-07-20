""" .user_infoファイル操作クラス
"""

import os
import json
import requests
from ..gin import sync

def get_user_id():
    """$HOME/.user_infoからユーザーIDを取得する。
    RETURN
    -----------------
    user_id : str
        Description : ユーザーID
    """
    os.chdir(os.environ['HOME'])
    file_path = '.user_info.json'
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
    params = {}
    with open(sync.fetch_param_file_path(), mode='r') as f:
        params = json.load(f)

    # ユーザー名からuidを取得する
    baseURL = params['siblings']['ginHttp'] + '/api/v1/users/'
    response = requests.get(baseURL + name)
    uid = response.json()['id']

    user_info = {"user_id":uid}
    with open('/home/jovyan/.user_info.json', 'w') as f:
        json.dump(user_info, f, indent=4)