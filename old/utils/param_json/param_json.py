
from http import HTTPStatus
from ..gin_api import api
import json
from ... utils import display_util
from ..gin_api import repos_search

from urllib import parse

import os
os.chdir('/home/jovyan/WORKFLOWS')
from utils.common import common

param_file_path = '/home/jovyan/WORKFLOWS/FLOW/param_files/params.json'


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

            f = open(param_file_path, 'r')
            df = json.load(f)
            f.close()

            response_data = response.json()
            http_url = response_data["http"]
            if http_url[-1] == '/':
                http_url = http_url.rstrip('/')

            df["siblings"]["ginHttp"] = http_url
            df["siblings"]["ginSsh"] = response_data["ssh"]

            with open(param_file_path, 'w') as f:
                json.dump(df, f, indent=4)

            display_util.display_info("データガバナンス機能のサーバ情報の更新が完了しました。次に進んでください。")

        elif response.status_code == HTTPStatus.NOT_FOUND:
            retry_num -= 1
            if retry_num == 0:
                display_util.display_err("データガバナンス機能から正しいデータが取得できませんでした。システム担当者にご連絡ください。")
                flg = False