"""GIN_API : api/v1/repos/search Servise method
    参照:utils.gin_api.api.py repos_search()
"""

from ..repository_id import repository_id
from ...except_class import query_err
from ..gin_api import api


def get_new_user_repo_nm(scheme, domain):
    """リポジトリIDからGIN fork上の現在のuserNm/repoNmの値を取得する。
    ARG
    ---------------
    scheme : str
        Description : プロトコル名(http, https, ssh)
    domain : str
        Description : ドメイン名

    RETURN
    ---------------
    full_name : str
        Description : userNm/repoNm (リポジトリオーナ名/リポジトリ名)

    EXCEPTION
    ---------------
    query_err.QueryError() :
        Description : レスポンス "data"内のデータ数が１以外の場合不正なクエリとして例外とする
    requests.exceptions.RequestException :
        Description : 接続の確立不良。
        From : 下位モジュール

    """
    # リポジトリidを取得
    repo_id = repository_id.get_repo_id()

    res_data = api.repos_search_by_repo_id(scheme, domain, repo_id)

    if len(res_data["data"]) == 1:
        full_name: str = res_data["data"][0]["full_name"]
        return full_name
    else:
        raise query_err.QueryError()
