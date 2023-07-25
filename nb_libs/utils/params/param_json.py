import os
import json
from http import HTTPStatus
from urllib import parse
from ..gin import api
from ..message import display, message
from ..common import common
from ..path import path


PARAM_FILE_PATH = os.path.join(path.DATA_PATH, 'params.json')


def get_params()->dict:
    """params.jsonからパラメータを取得する。

    RETURN
    -----------------
    params : dict
        Description : parameter for connection
    """
    with open(PARAM_FILE_PATH, mode='r') as f:
            params = json.load(f)
    return params


def update_param_url(remote_origin_url):
    """param.jsonのsiblings.ginHttpとsiblings.ginSshを更新する。

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

    pr = parse.urlparse(adjust_url)
    retry_num = 6
    flg = True
    while flg:
        response = api.get_server_info(pr.scheme, pr.netloc)
        if response.status_code == HTTPStatus.OK:
            flg = False

            f = open(PARAM_FILE_PATH, 'r')
            df = json.load(f)
            f.close()

            response_data = response.json()
            http_url = response_data["http"]
            if http_url[-1] == '/':
                http_url = http_url.rstrip('/')

            df["siblings"]["ginHttp"] = http_url
            df["siblings"]["ginSsh"] = response_data["ssh"]

            with open(PARAM_FILE_PATH, 'w') as f:
                json.dump(df, f, indent=4)

            display.display_info(message.get('param_json','success'))

        elif response.status_code == HTTPStatus.NOT_FOUND:
            retry_num -= 1
            if retry_num == 0:
                flg = False
                display.display_err(message.get('param_json','not_found_error'))
                raise Exception
