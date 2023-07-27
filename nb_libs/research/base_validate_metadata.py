
import requests
from utils.params import repository_id, token, param_json
from utils.git import git_module
from utils.message import display, message
from utils.except_class import DidNotFinishError, UnexpectedError, DGTaskError, ExecCmdError
import requests
from utils.repo_metadata import metadata
from utils.gin import api as gin_api
from urllib import parse
from typing import Any
from http import HTTPStatus

def prepare_matadata()->Any:
    # リポジトリIDの用意
    try:
        repo_id = repository_id.get_repo_id()
    except FileNotFoundError as e:
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('repository_id', 'no_exist')
        display.display_err(err_format.format(reason))
        raise DGTaskError() from e


    # GIN-forkトークンの用意
    try:
        gin_api_token = token.get_ginfork_token()
    except FileNotFoundError as e:
        # .token.jsonが存在しない場合
        err_format = message.get('DEFAULT', 'not_finish_setup_format')
        reason = message.get('token', 'no_exist')
        display.display_err(err_format.format(reason))
        raise DGTaskError() from e
    except KeyError as e:
        # .token.jsonファイルに『ginfork_token』キーが存在しない場合
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('token', 'no_key_ginfork_token')
        display.display_err(err_format.format(reason))
        raise DGTaskError() from e
    except Exception as e:
        # 想定外のエラーの場合
        msg = message.get('DEFAULT', 'unexpected')
        display.display_err(msg)
        raise DGTaskError() from e


    # GIN-forkHTTP-URLの用意
    try:
        gin_http = param_json.get_gin_http()
    except FileNotFoundError as e:
        # params.jsonが存在しない場合
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('param_json', 'no_exist')
        display.display_err(err_format.format(reason))
        raise DGTaskError() from e
    except KeyError as e:
        # params.jsonにキーが存在しない場合
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('param_json', 'no_key_gin_http')
        display.display_err(err_format.format(reason))
        raise DGTaskError() from e
    except Exception as e:
        # 想定外のエラーの場合
        msg = message.get('DEFAULT', 'unexpected')
        display.display_err(msg)
        raise DGTaskError() from e



    # 現在のブランチを取得する
    try :
        branch = git_module.get_current_branch()
    except ExecCmdError as e:
        # git branchコマンド実行失敗の場合
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('git', 'fail_get_branch')
        display.display_err(err_format.format(reason))
        raise DGTaskError() from e
    except Exception as e:
        # 想定外のエラーの場合
        msg = message.get('DEFAULT', 'unexpected')
        display.display_err(msg)
        raise DGTaskError() from e

    # リポジトリメタデータを取得
    try :
        pr = parse.urlparse(gin_http)
        response = gin_api.get_repo_metadata(
            scheme=pr.scheme,
            domain=pr.netloc,
            token=gin_api_token,
            repo_id=repo_id,
            branch=branch)
        if response.status_code == HTTPStatus.OK:
            # 200 OK -> GIN-forkリポジトリメタデータの返却
            return response.json()
        else:
            # GIN-forkリポジトリメタデータが取得できない場合
            msg = message.get('DEFAULT', 'unexpected')
            display.display_err(msg)
            raise DGTaskError('Fail Getting GIN-fork Repository Metadata. GIN-fork API [api/v1/repos/:repo_id/:branch_name:/metadata]')
    except requests.exceptions.RequestException as e:
        # GIN-forkへの通信不良
        msg = message.get('DEFAULT', 'gin_connection_error')
        display.display_err(msg)
        raise DGTaskError() from e
    except Exception as e:
        # 想定外のエラーの場合
        msg = message.get('DEFAULT', 'unexpected')
        display.display_err(msg)
        raise DGTaskError() from e

def not_exec_pre_cell():
    msg = message.get('nb_exec', 'not_exec_pre_cell')
    display.display_err(msg)
    raise DGTaskError('The immediately preceding cell may not have been executed')


def pkg_metadata(raw_metadata)->Any:
