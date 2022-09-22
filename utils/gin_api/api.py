"""
GIN frok APIの通信メソッド群
"""

from urllib import parse
import requests


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


def repos(scheme, domain, owner_repo_nm):
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
    return requests.get(api_url)
