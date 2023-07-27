
import requests
from utils.params import repository_id, token, param_json
from utils.git import git_module
from utils.message import display as msg_display, message
from utils.except_class import DidNotFinishError, UnexpectedError, DGTaskError, ExecCmdError
from utils.dg_core import api as core_api
from utils.path import path
import requests
from utils.repo_metadata import metadata
from utils.gin import api as gin_api
from utils.common import raise_error
from urllib import parse
from typing import Any
from http import HTTPStatus
from dg_packager.ro_generator.gin_ro_generator import GinRoGenerator
from dg_packager.error.error import JsonValidationError, RoPkgError
import os
import time
import json
import panel as pn
from IPython.display import clear_output, display


def prepare_matadata()->Any:
    # リポジトリIDの用意
    try:
        repo_id = repository_id.get_repo_id()
    except FileNotFoundError as e:
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('repository_id', 'no_exist')
        msg_display.display_err(err_format.format(reason))
        raise DGTaskError() from e


    # GIN-forkトークンの用意
    try:
        gin_api_token = token.get_ginfork_token()
    except FileNotFoundError as e:
        # .token.jsonが存在しない場合
        err_format = message.get('DEFAULT', 'not_finish_setup_format')
        reason = message.get('token', 'no_exist')
        msg_display.display_err(err_format.format(reason))
        raise DGTaskError() from e
    except KeyError as e:
        # .token.jsonファイルに『ginfork_token』キーが存在しない場合
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('token', 'no_key_ginfork_token')
        msg_display.display_err(err_format.format(reason))
        raise DGTaskError() from e
    except Exception as e:
        # 想定外のエラーの場合
        msg = message.get('DEFAULT', 'unexpected')
        msg_display.display_err(msg)
        raise DGTaskError() from e


    # GIN-forkHTTP-URLの用意
    try:
        gin_http = param_json.get_gin_http()
    except FileNotFoundError as e:
        # params.jsonが存在しない場合
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('param_json', 'no_exist')
        msg_display.display_err(err_format.format(reason))
        raise DGTaskError() from e
    except KeyError as e:
        # params.jsonにキーが存在しない場合
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('param_json', 'no_key_gin_http')
        msg_display.display_err(err_format.format(reason))
        raise DGTaskError() from e
    except Exception as e:
        # 想定外のエラーの場合
        msg = message.get('DEFAULT', 'unexpected')
        msg_display.display_err(msg)
        raise DGTaskError() from e



    # 現在のブランチを取得する
    try :
        branch = git_module.get_current_branch()
    except ExecCmdError as e:
        # git branchコマンド実行失敗の場合
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('git', 'fail_get_branch')
        msg_display.display_err(err_format.format(reason))
        raise DGTaskError() from e
    except Exception as e:
        # 想定外のエラーの場合
        msg = message.get('DEFAULT', 'unexpected')
        msg_display.display_err(msg)
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
            msg = message.get('metadata', 'get_metadata')
            msg_display.display_info(msg)
            return response.json()
        else:
            # GIN-forkリポジトリメタデータが取得できない場合
            msg = message.get('DEFAULT', 'unexpected')
            msg_display.display_err(msg)
            raise DGTaskError('Fail Getting GIN-fork Repository Metadata. GIN-fork API [api/v1/repos/:repo_id/:branch_name:/metadata]')
    except requests.exceptions.RequestException as e:
        # GIN-forkへの通信不良
        msg = message.get('DEFAULT', 'gin_connection_error')
        msg_display.display_err(msg)
        raise DGTaskError() from e
    except Exception as e:
        # 想定外のエラーの場合
        msg = message.get('DEFAULT', 'unexpected')
        msg_display.display_err(msg)
        raise DGTaskError() from e

def not_exec_pre_cell():
    msg = message.get('nb_exec', 'not_exec_pre_cell')
    msg_display.display_err(msg)
    raise DGTaskError('The immediately preceding cell may not have been executed')


def pkg_metadata(metadata)->Any:

    # convert GIN-fork metadata to ro-crate
    try:
        ro_crate =GinRoGenerator.Generate(raw_metadata=metadata)
        msg = message.get('metadata', 'complete_pkg')
        msg_display.display_info(msg)
        return ro_crate
    except JsonValidationError as e:
        # if given Raw Metadata to Function is invalid format, exception occurs.(derived dg-packager)
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('metadata', 'invaild_metadata_format')
        msg_display.display_err(err_format.format(reason))
        raise DGTaskError() from e
    except RoPkgError as e:
        # if each value of metadata is invalid on checking property, exception occurs.(derived SDK Library)
        if "{'<ginfork.GinMonitoring #ginmonitoring>': {'experimentPackageList': 'This property is required, but not found.'}" in str(e):
            # no exist ex pkg
            msg = message.get('metadata', 'no_exist_ex_pkg')
            msg_display.display_err(msg)
            raise DGTaskError() from e
        else:
            # if metadata is incomplete
            msg = message.get('metadata', 'incomplete_metadata')
            msg_display.display_err(msg)
            raise DGTaskError() from e
    except Exception as e:
        # if unexpected errors
        msg = message.get('DEFAULT', 'unexpected')
        msg_display.display_err(msg)
        raise DGTaskError() from e

def verify_metadata(ro_crate)->Any:

    # get scheme and netloc of DG-Core
    try:
        scheme, netloc = param_json.get_core_scheme_netloc()
    except FileNotFoundError as e:
        # params.jsonが存在しない場合
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('param_json', 'no_exist')
        msg_display.display_err(err_format.format(reason))
        raise DGTaskError() from e
    except KeyError as e:
        # params.jsonにキーが存在しない場合
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('param_json', 'no_key_core_http')
        msg_display.display_err(err_format.format(reason))
        raise DGTaskError() from e
    except Exception as e:
        # 想定外のエラーの場合
        msg = message.get('DEFAULT', 'unexpected')
        msg_display.display_err(msg)
        raise DGTaskError() from e

    # request validation
    try :
        response = core_api.verify_metadata(scheme=scheme, netloc=netloc, ro_crate=ro_crate)
        req_body = response.json()
        if response.status_code == HTTPStatus.OK:
            # 200 OK(Successful validation request)
            ## record request_id
            request_id = req_body['request_id']
            tmp_save_request_id(request_id)
            return True
        else:
            # 想定外のエラーの場合
            msg = message.get('DEFAULT', 'unexpected')
            msg_display.display_err(msg)
            raise DGTaskError('The request to the metadata validation service failed. [ERROR] : {}'.format(req_body['message']))
    except requests.exceptions.RequestException as e:
        # DG-Coreへの通信不良
        msg = message.get('metadata', 'core_connection_error')
        msg_display.display_err(msg)
        raise DGTaskError() from e
    except Exception as e:
        # 想定外のエラーの場合
        msg = message.get('DEFAULT', 'unexpected')
        msg_display.display_err(msg)
        raise DGTaskError() from e




def show_verification_result():
    # get request id from .tmp/validation/request_id.txt
    try :
        request_id = get_request_id()
    except FileNotFoundError as e:
        # params.jsonが存在しない場合
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('metadata', 'no_exist_req_id_file')
        msg_display.display_err(err_format.format(reason))
        raise DGTaskError() from e

    # get scheme and netloc of DG-Core
    try:
        scheme, netloc = param_json.get_core_scheme_netloc()
    except FileNotFoundError as e:
        # params.jsonが存在しない場合
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('param_json', 'no_exist')
        msg_display.display_err(err_format.format(reason))
        raise DGTaskError() from e
    except KeyError as e:
        # params.jsonにキーが存在しない場合
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('param_json', 'no_key_core_http')
        msg_display.display_err(err_format.format(reason))
        raise DGTaskError() from e
    except Exception as e:
        # 想定外のエラーの場合
        msg = message.get('DEFAULT', 'unexpected')
        msg_display.display_err(msg)
        raise DGTaskError() from e

    # get verification result from DG-Core
    try:
        counter = 10
        while counter >0:
            counter -= 1
            clear_output()
            response = core_api.get_verification_result(scheme=scheme, netloc=netloc,request_id=request_id)
            req_body = response.json()
            if response.status_code == HTTPStatus.OK:
                status = req_body['status']

                if status == 'UNKNOWN':
                    err_format = message.get('DEFAULT', 'unexpected_errors_format')
                    reason = message.get('metadata', 'no_exist_req')
                    msg_display.display_err(err_format.format(reason.format(request_id)))
                    break

                elif any([status == 'QUEUED', status == 'RUNNING']):
                    msg = message.get('metadata', 'repeate_req')
                    msg_display.display_warm(msg.format(request_id))
                    time.sleep(5)
                    continue

                elif status == 'COMPLETE':
                    # save result
                    save_verification_results(req_body)
                    msg = message.get('metadata', 'verification_ok')
                    msg_display.display_info(msg)
                    break

                elif status == 'FAILED':
                    # save result
                    save_verification_results(req_body)
                    msg = message.get('metadata', 'verification_ng')
                    msg_display.display_info(msg)
                    output_result(request_id)
                    break

                elif status == 'EXECUTOR_ERROR':
                    err_format = message.get('DEFAULT', 'unexpected_errors_format')
                    reason = message.get('metadata', 'terminated_abnormally')
                    msg_display.display_err(err_format.format(reason))
                    break

                elif status == 'CANCELING':
                    err_format = message.get('DEFAULT', 'unexpected_errors_format')
                    reason = message.get('metadata', 'canceling')
                    msg_display.display_err(err_format.format(reason.format(request_id)))
                    break

                elif status == 'CANCELED':
                    err_format = message.get('DEFAULT', 'unexpected_errors_format')
                    reason = message.get('metadata', 'cancel')
                    msg_display.display_err(err_format.format(reason.format(request_id)))
                    break

            else:
                # Other than 200 OK
                # Unexpected errors
                msg = message.get('DEFAULT', 'unexpected')
                msg_display.display_err(msg)
                raise DGTaskError('The request to the metadata validation service failed. [ERROR] : {}'.format(req_body['message']))
        else:
            clear_output()
            # Re-execution is required
            msg = message.get('metadata', 'exec_cell_repeate')
            msg_display.display_warm(msg)
            return
    except requests.exceptions.RequestException as e:
        # DG-Coreへの通信不良
        err_format = message.get('DEFAULT', 'unexpected_errors_format')
        reason = message.get('metadata', 'core_connection_error')
        msg_display.display_err(err_format.format(reason))
        return
    except Exception as e:
        # 想定外のエラーの場合
        msg = message.get('DEFAULT', 'unexpected')
        msg_display.display_err(msg)
        raise DGTaskError() from e


def tmp_save_request_id(request_id):
    """Save in the temporary folder of the verification ID(request id)

    Args:
        request_id (str): [verification ID]
    """

    if not os.path.exists(path.TMP_DIR):
        # If there is no .tmp folder, create one.
        os.makedirs(path.TMP_DIR)

    if not os.path.exists(path.TMP_VALIDATION_DIR):
        # If there is no .tmp/validation folder, create one.
        os.makedirs(path.TMP_VALIDATION_DIR)

    # Record the verification ID. If the file already exists, overwrite it.
    file_path = path.REQUEST_ID_FILE_PATH
    with open(file_path, 'w') as f:
        f.write(request_id)


def get_request_id()->str:
    """get request ID
    RETURN
    -----------------
    request_id : str
        Description : Request ID obtained from the response of the verification request API
    """
    file_path = path.REQUEST_ID_FILE_PATH
    with open(file_path, 'r') as f:
        request_id = f.read()
    return request_id


RO_CRATE_FILE_NAME = 'ro_crate.json'
ENTITY_IDS_FILE_NAME = 'entity_ids.json'
RESULTS_FILE_NAME = 'results.json'

def save_verification_results(result):
    """write the verification results in .tmp/validation/{request_id}
    RETURN
    -----------------
    """
    request_id = get_request_id()
    vaid_dir = path.TMP_VALIDATION_DIR

    tmp_result_folder = os.path.join(vaid_dir, request_id)

    if not os.path.exists(tmp_result_folder):
        os.makedirs(tmp_result_folder)

    tmp_files = [
        [result['request']['roCrate'], os.path.join(tmp_result_folder, RO_CRATE_FILE_NAME)],
        [result['request']['entityIds'], os.path.join(tmp_result_folder, ENTITY_IDS_FILE_NAME)],
        [result['results'], os.path.join(tmp_result_folder, RESULTS_FILE_NAME)]
    ]
    for file in tmp_files:
        with open(file[1], 'w', encoding='utf-8') as f:
            json.dump(file[0], f, indent=4, ensure_ascii=False)


def output_result(request_id):
    tmp_result_path = os.path.join(path.TMP_VALIDATION_DIR, request_id, RESULTS_FILE_NAME)
    with open(tmp_result_path, 'r') as f:
        result = f.read()
    msg_display.display_msg(result)


def select_done_save():
    pn.extension()

    option = {}
    # generate options
    option[message.get('metadata', 'record')] = 0
    option[message.get('metadata', 'non_record')] = 1

    # プルダウン形式のセレクターを生成
    menu_selector = pn.widgets.Select(name=message.get('metadata', 'record_form'), options=option, value=0, width=350)
    done_button = pn.widgets.Button(name= "選択を完了する", button_type= "primary")
    html_output = pn.pane.HTML()

    def selected(event):
        selected_value = event.new

        if selected_value == 0:
            # record
            ## copy tmp file to repository

            ## del tmp file
            done_button.button_type = 'success'
            done_button.name = message.get('metadata', 'complete_prepare_sync')
            pass
        elif selected_value == 1:
            # not record
            ## del tmp file

            done_button.button_type = 'success'
            done_button.name = message.get('metadata', 'complete_del_verification_data')
            pass
        else:
            # undefined
            done_button.button_type = 'danger'
            done_button.name = message.get('DEFAULT', 'unexpected')
            html_output.object = msg_display.creat_html_msg(msg=message.get('metadata', 'undefined_option'),fore='#ff0000',tag='p')
            html_output.height = 30
            html_output.width = 900
            pass

    done_button.on_click(selected)


    display(pn.Column(menu_selector, done_button, html_output))
