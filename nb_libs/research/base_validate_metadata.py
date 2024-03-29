import shutil
import requests
import os
import time
import json
import requests
from urllib import parse
from typing import Any
from http import HTTPStatus

import panel as pn
from dg_packager.ro_generator.gin_ro_generator import GinRoGenerator
from dg_packager.error.error import JsonValidationError, RoPkgError
from IPython.display import clear_output, display

from ..utils.params import repository_id, token, param_json
from ..utils.git import git_module
from ..utils.message import display as msg_display, message
from ..utils.except_class import DGTaskError, ExecCmdError
from ..utils.dg_core import api as core_api
from ..utils.path import path
from ..utils.common import raise_error
from ..utils.gin import api as gin_api
from ..utils.flow.module import check_finished_setup_research
# To remove the git config warning message on module import with execution result
clear_output()

def prepare_matadata()->Any:
    is_finished = check_finished_setup_research()
    if not is_finished:
        err_msg = message.get('DEFAULT', 'not_finish_setup')
        msg_display.display_warm(err_msg)
        raise DGTaskError('Initial setup has not been completed.')

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

def not_exec_pre_cell_raise():
    raise_error.not_exec_pre_cell_raise()

def not_exec_pre_cell():
    msg = message.get('nb_exec', 'not_exec_pre_cell')
    msg_display.display_err(msg)


def pkg_metadata(metadata)->Any:

    # convert GIN-fork metadata to ro-crate
    try:
        ro_crate = GinRoGenerator.Generate(raw_metadata=metadata)
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
            msg = message.get('metadata', 'complete_verification_req')
            msg_display.display_info(msg)
            msg_display.display_msg(message.get('metadata', 'show_req_id').format(request_id))
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
                    return True

                elif status == 'FAILED':
                    # save result
                    save_verification_results(req_body)
                    msg = message.get('metadata', 'verification_ng')
                    msg_display.display_info(msg)
                    output_result(request_id)
                    return True

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
                msg_display.display_err('The request to the metadata validation service failed. [ERROR] : {}'.format(req_body['message']))
                continue
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

    tmp_result_folder = os.path.join(path.TMP_VALIDATION_DIR, request_id)

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


def get_non_saving_data():
    return message.get('metadata', 'non_saving_data')


def has_result_in_tmp():
    """Existence check of the validation result file set

    Returns:
        [bool]: [True : exist, False : not exist]
    """

    # get request id from .tmp/validation/request_id.txt
    try :
        request_id = get_request_id()
    except FileNotFoundError:
        warm_err = get_non_saving_data()
        msg_display.display_err(warm_err)
        return False

    # check having 3 validated results
    ## .tmp/validation/:request_id/
    tmp_result_folder = os.path.join(path.TMP_VALIDATION_DIR, request_id)
    ### ro_crate.json
    if not os.path.isfile(os.path.join(tmp_result_folder, RO_CRATE_FILE_NAME)):
        # ro_crate.json does not exist
        warm_err = get_non_saving_data()
        msg_display.display_err(warm_err)
        return False
    ### entity_ids.json
    if not os.path.isfile(os.path.join(tmp_result_folder, ENTITY_IDS_FILE_NAME)):
        # entity_ids.json does not exist
        warm_err = get_non_saving_data()
        msg_display.display_err(warm_err)
        return False
    ### results.json
    if not os.path.isfile(os.path.join(tmp_result_folder, RESULTS_FILE_NAME)):
        # results.json does not exist
        warm_err = get_non_saving_data()
        msg_display.display_err(warm_err)
        return False

    return True

def del_result_in_tmp():
    """delete temporary validation-related files(.tmp/validation/{request_id}/*, .tmp/validation/request_id.txt)
    """

    # get request id from .tmp/validation/request_id.txt
    try :
        request_id = get_request_id()
        # delete .tmp/validation/:request_id
        ## .tmp/validation/:request_id/
        tmp_result_folder = os.path.join(path.TMP_VALIDATION_DIR, request_id)
        if os.path.exists(tmp_result_folder):
            shutil.rmtree(tmp_result_folder)
        # delete .tmp/validation/request_id.txt
        request_id_file_path = path.REQUEST_ID_FILE_PATH
        if os.path.exists(request_id_file_path):
            os.remove(request_id_file_path)
    except FileNotFoundError:
        pass

def copy_tmp_results_to_repository():
    """Copy the set of validation result files in the temporary folder to the repository.
    """

    # get request id from .tmp/validation/request_id.txt
    request_id = get_request_id()


    repo_result_dir = path.VALIDATION_RESULTS_DIR_PATH
    # If the repository does not have a folder for storing verification results, create one.
    if not os.path.exists(repo_result_dir):
            os.makedirs(repo_result_dir)

    tmp_result_dir = os.path.join(path.TMP_VALIDATION_DIR, request_id)

    for file in os.listdir(tmp_result_dir):
        src_file_path = os.path.join(tmp_result_dir, file)
        dst_file_path = os.path.join(repo_result_dir, file)
        shutil.copyfile(src_file_path, dst_file_path)


def select_done_save():
    # Check if the verification result exists in the temporary folder
    has_ok = has_result_in_tmp()
    if not has_ok :
        # If there is no verification result, the previous cell may not have been executed
        return

    # The data to be saved exists.
    # Generate and display selection forms
    pn.extension()

    record = message.get('metadata', 'record')
    non_record = message.get('metadata', 'non_record')
    option = [record, non_record]
    # generate options
    # option[message.get('metadata', 'record')] = 0
    # option[message.get('metadata', 'non_record')] = 1

    # プルダウン形式のセレクターを生成
    menu_selector = pn.widgets.Select(name=message.get('metadata', 'record_form'), options=option, width=350)
    done_button = pn.widgets.Button(name=message.get('metadata', 'end_choose'), button_type= "default")
    html_output = pn.pane.HTML()

    def selected(event):
        selected_value = menu_selector.value

        if selected_value == record:
            # record
            ## Record selection information.
            record_selection_info(True)
            done_button.button_type = 'success'
            selected_name = message.get('metadata', 'record')
            done_button.name = message.get('metadata', 'reception_completed').format(selected_name)
            return
        elif selected_value == non_record:
            # not record
            ## Record selection information.
            record_selection_info(False)
            done_button.button_type = 'success'
            selected_name = message.get('metadata', 'non_record')
            done_button.name = message.get('metadata', 'reception_completed').format(selected_name)
            return
        else:
            # undefined
            done_button.button_type = 'danger'
            done_button.name = message.get('DEFAULT', 'unexpected')
            html_output.object = msg_display.creat_html_msg(msg=message.get('metadata', 'undefined_option'),fore='#ff0000',tag='p')
            html_output.height = 30
            html_output.width = 900
            return

    done_button.on_click(selected)

    display(pn.Column(menu_selector, done_button, html_output))

RF_FORM_DATA_FILE = 'base_validate_metadata.json'

def record_selection_info(need_sync:bool):

    # generate path (.tmp/rf_form_data/base_validate_metadata.json)
    form_data_dir = path.RF_FORM_DATA_DIR
    if not os.path.exists(form_data_dir):
            os.makedirs(form_data_dir)

    form_data_path = os.path.join(form_data_dir, RF_FORM_DATA_FILE)

    data = {'need_sync' : need_sync}
    with open(form_data_path, 'w') as f:
        json.dump(data, f, indent=4)

def del_selection_info_file():
    form_data_path = os.path.join(path.RF_FORM_DATA_DIR, RF_FORM_DATA_FILE)
    if os.path.exists(form_data_path):
        os.remove(form_data_path)

def sync():

    form_data_path = os.path.join(path.RF_FORM_DATA_DIR, RF_FORM_DATA_FILE)

    if os.path.exists(form_data_path):
        with open(form_data_path) as f:
            data = json.load(f)
        value = data['need_sync']

        if value:
            # Synchronization required verification results
            msg = message.get('metadata', 'save_verification_and_execution_result')
            msg_display.display_info(msg)
        else:
            # No synchronization required
            msg = message.get('metadata', 'save_execution_result')
            msg_display.display_info(msg)
        return value
    else:
        # If the selection information file does not exist
        # No previous cell has been executed.
        msg = message.get('nb_exec', 'not_exec_pre_cell')
        msg_display.display_err(msg)
        return None


def prepare_sync_arg(mode : bool) -> tuple[list[str], str]:
    """Create the necessary information for synchronization

    Args:
        mode (bool): [True : Synchronize verification results, Flase : No synchronization of verification results required]
    """

    # create git path
    git_path = []

    if mode:
        ## copy tmp file to repository
        copy_tmp_results_to_repository()
        ## add /home/jovyan/validation_results
        git_path.append(path.VALIDATION_RESULTS_DIR_PATH)

    ## this task notebook
    git_path.append(os.path.join(path.RES_DIR_PATH, path.BASE_VALIDATE_METADATA))

    commit_msg = 'メタデータ検証'

    return git_path, commit_msg

def clean_up(is_finish_sync:bool):
    if is_finish_sync:
        # delete .tmp/request_id.txt and .tmp/validation/{request_id}/*
        del_result_in_tmp()
        # delete .tmp/rf_form_data/base_validate_metadata.json
        del_selection_info_file()
    else :
        pass
