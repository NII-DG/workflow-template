"""
GIN frok APIの通信メソッド群
"""

from urllib import parse
import requests
import os
import json
import sys
from ..message import display
from ..params import user_info
import sync


def repos_search_by_repo_id(scheme, domain, repo_id):
    """GIN_API : api/v1/repos/search リクエストメソッド

    ARG
    ---------------
    scheme : str
        Description : プロトコル名(http, https, ssh)
    domain : str
        Description : ドメイン名
    repo_id : str
        Description : レポジトリID

    RETURN
    ---------------
    Respons :
        Description : レスポンスインスタンス

    EXCEPTION
    ---------------
    接続の確立不良 : requests.exceptions.RequestException
    """
    request_url = parse.urlunparse((scheme, domain, "api/v1/repos/search", "", "id=" + repo_id, ""))
    return requests.get(request_url)


def repos(scheme, domain, owner_repo_nm, token=''):
    """GIN_API : api/v1/repos/$repoOwnerNm/$repoNm リクエストメソッド

    ARG
    ---------------
    scheme : str
        Description : プロトコル名(http, https, ssh)
    domain : str
        Description : ドメイン名
    owner_repo_nm : str
        Description : リポジトリオーナ名/リポジトリ名

    RETURN
    ---------------
    Respons :
        Description : レスポンスインスタンス

    EXCEPTION
    ---------------
    接続の確立不良 : requests.exceptions.RequestException
    """

    sub_url = parse.urljoin("api/v1/repos/", "./" + owner_repo_nm)
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    if len(token) > 0:
        params = {'token' : token}
        return requests.get(url=api_url, params=params)
    else:
        return requests.get(url=api_url)

def delete_access_token(scheme, domain, token):
    sub_url = "api/v1/user/token/delete"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    params = {'token' : token}
    return requests.delete(url=api_url, params=params)

def create_token_for_launch(scheme, domain, token):
    sub_url = "api/v1/user/token/forlaunch"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    params = {'token' : token}
    return requests.post(url=api_url, params=params)

def get_server_info(scheme, domain):
    sub_url = "api/v1/gin"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    return requests.get(url=api_url)



def add_container(experiment_title=""):
    """register add container to GIN-fork container list.

    ARG
    ---------------
    experiment_title : str
        Description : a contaier is regarded as an experiment contaier if and only if experiment_title is set.

    RETURN
    ---------------
    Returns nothing.

    EXCEPTION
    ---------------
    """

    uid = str(user_info.get_user_id())
    with open(os.environ['HOME'] + '/.repository_id', 'r') as f:
        repo_id = f.read()
    with open(sync.fetch_param_file_path(), mode='r') as f:
        params = json.load(f)
    with open('/home/jovyan/.token.json', 'r') as f:
        dic = json.load(f)
        token = dic["ginfork_token"]

    # experiment
    if len(experiment_title) > 0:
        response = requests.post(
            params['siblings']['ginHttp']+'/api/v1/container?token=' + token,
            data={
                "repo_id": repo_id,
                "user_id": uid,
                "server_name": os.environ["JUPYTERHUB_SERVICE_PREFIX"].split('/')[3],
                "experiment_package" : experiment_title,
                "url": "https://jupyter.cs.rcos.nii.ac.jp" + os.environ["JUPYTERHUB_SERVICE_PREFIX"] + "notebooks/WORKFLOWS/experiment.ipynb"
            })

    # research
    else:
        response = requests.post(
            params['siblings']['ginHttp']+'/api/v1/container?token=' + token,
            data={
                "repo_id": repo_id,
                "user_id": uid,
                "server_name": os.environ["JUPYTERHUB_SERVICE_PREFIX"].split('/')[3],
                "url": "https://jupyter.cs.rcos.nii.ac.jp" + os.environ["JUPYTERHUB_SERVICE_PREFIX"] + "notebooks/WORKFLOWS/base_FLOW.ipynb"
            })

    try:
        if response.status_code == requests.codes.ok:
            display.display_info('実行環境を追加しました。')
        elif response.json()["error"].startswith("Error 1062"):
            display.display_warm('すでに追加されています。')
        else:
            display.display_err('追加に失敗しました。再度実行してください。')

    except Exception:
        display.display_err('追加に失敗しました。再度実行してください。')


def patch_container():
    """update only updated_unix of container

    ARG
    ---------------
    experiment_title : str
        Description : contaier is regarded as experiment contaier if and only if experiment_title is set.

    RETURN
    ---------------
    Returns nothing.

    EXCEPTION
    ---------------
    """

    uid = str(user_info.get_user_id())
    with open(sync.fetch_param_file_path(), mode='r') as f:
        params = json.load(f)
    with open('/home/jovyan/.token.json', 'r') as f:
        dic = json.load(f)
        token = dic["ginfork_token"]
    server_name = os.environ["JUPYTERHUB_SERVICE_PREFIX"].split('/')[3]

    requests.patch(
        params['siblings']['ginHttp'] + f'/api/v1/container?token={token}&server_name={server_name}&user_id={uid}'
    )


def delete_container():
    """logical delete of container

    ARG
    ---------------

    RETURN
    ---------------
    Returns nothing.

    EXCEPTION
    ---------------
    """

    uid = str(user_info.get_user_id())
    with open(sync.fetch_param_file_path(), mode='r') as f:
        params = json.load(f)
    with open('/home/jovyan/.token.json', 'r') as f:
        dic = json.load(f)
        token = dic["ginfork_token"]
    server_name = os.environ["JUPYTERHUB_SERVICE_PREFIX"].split('/')[3]

    response = requests.delete(
        params['siblings']['ginHttp'] + f'/api/v1/container?token={token}&server_name={server_name}&user_id={uid}'
    )

    if response.status_code == requests.codes.ok:
        display.display_info('実行環境の削除を反映しました。')
    else:
        display.display_err('削除の反映に失敗しました。再度実行してください。')
