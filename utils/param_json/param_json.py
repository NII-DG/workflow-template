
from http import HTTPStatus
from ..gin_api import api
import json
from ... utils import display_util
from ..gin_api import repos_search

from urllib import parse

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
    query_err.QueryError :
        Description : レスポンス "data"内のデータ数が１以外の場合不正なクエリとして例外とする
        From : 下位モジュール

    """

    pr = parse.urlparse(remote_origin_url)
    owner_repo_nm = pr.path.replace(".git", "")
    retry_num = 6
    flg = True
    while flg:
        response = api.repos(pr.scheme, pr.netloc, owner_repo_nm)
        if response.status_code == HTTPStatus.OK:
            flg = False
            response_data = response.json()
            pr_http = parse.urlparse(response_data["html_url"])
            pr_ssh = parse.urlparse(response_data["ssh_url"])

            f = open(param_file_path, 'r')
            df = json.load(f)
            f.close()

            df["siblings"]["ginHttp"] = parse.urlunparse((pr_http.scheme, pr_http.netloc, "", "", "", ""))
            df["siblings"]["ginSsh"] = parse.urlunparse((pr_ssh.scheme, pr_ssh.netloc, "", "", "", ""))

            with open(param_file_path, 'w') as f:
                json.dump(df, f, indent=4)

            display_util.display_info("データガバナンス機能のサーバ情報を更新が完了しまいた。次の進んでください")

        elif response.status_code == HTTPStatus.NOT_FOUND:
            retry_num -= 1
            if retry_num == 0:
                display_util.display_err("データガバナンス機能から正しいデータが取得できませんでした。システム担当者にご連絡ください   : nm" + owner_repo_nm)
                flg = False
            else:
                owner_repo_nm = repos_search.get_new_user_repo_nm(pr.scheme, pr.netloc)
