"""
GIN frok APIの通信メソッド群
"""
from urllib import parse
import requests
import time


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


def upload_key(scheme:str, domain:str, token:str, pubkey:str):
    """GIN_API : api/v1/user/keys リクエストメソッド

    ARG
    ---------------
    scheme : str
        Description : プロトコル名(http, https, ssh)
    domain : str
        Description : ドメイン名
    token : str
        Description : token
    pubkey : str
        Description : SSHのpublic key

    RETURN
    ---------------
    Respons :
        Description : レスポンスインスタンス

    EXCEPTION
    ---------------
    接続の確立不良 : requests.exceptions.RequestException
    """
    sub_url = "api/v1/user/keys"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    params = {'token' : token}
    data={
        "title": "system-generated-"+str(time.time()),
        "key": pubkey
    }
    return requests.post(url=api_url, params=params,data=data)


def add_container(scheme, domain, token,
                    repo_id, user_id, server_name, ipynb_url, pkg_title=""):

    sub_url = "/api/v1/container"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    params = {'token' : token}
    data = {
            "repo_id": repo_id,
            "user_id": user_id,
            "server_name": server_name,
            "url":ipynb_url
    }
    if len(pkg_title) > 0:
        data["experiment_package"] = pkg_title

    return requests.post(url=api_url, params=params, data=data)


def patch_container(scheme, domain, token, server_name, user_id):
    sub_url = "/api/v1/container"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    params = {
        'token' : token,
        'server_name' : server_name,
        'user_id' : user_id
    }
    return requests.patch(url=api_url, params=params)


def delete_container(scheme, domain, token, server_name, user_id):
    sub_url = "/api/v1/container"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    params = {
        'token' : token,
        'server_name' : server_name,
        'user_id' : user_id
    }
    return requests.delete(url=api_url, params=params)