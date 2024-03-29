import os
import json
import shutil
import requests
import traceback
from pathlib import Path

import panel as pn
from IPython.display import clear_output, display

from ..utils.ex_utils import dmp, package as ex_pkg
from ..utils.common import common
from ..utils.form import prepare as pre
from ..utils.message import message as msg_mod, display as msg_display
from ..utils.params import ex_pkg_info, token
from ..utils.git import git_module
from ..utils.gin import sync, ssh, container
from ..utils.path import path as p
from ..utils.flow import module as flow
from ..utils.except_class import DidNotFinishError, Unauthorized


FILE_PATH = os.path.join(p.RF_FORM_DATA_DIR, 'required_every_time.json')
KEY_EX_PKG = 'ex_pkg_name'
KEY_EX_PARAM = 'param_ex_name'
KEY_CREATE_TEST = 'create_test_folder'
KEY_CREATE_CI = 'create_ci'


# ----- tmp_file handling -----
def set_params(ex_pkg_name:str, parama_ex_name:str, create_test_folder:bool, create_ci:bool):
    params_dict = {
    KEY_EX_PKG : ex_pkg_name,
    KEY_EX_PARAM : parama_ex_name,
    KEY_CREATE_TEST : create_test_folder,
    KEY_CREATE_CI : create_ci
    }
    common.create_json_file(FILE_PATH, params_dict)


def get_params():
    with open(FILE_PATH, mode='r') as f:
            params = json.load(f)
    return params


def delete_tmp_file():
    """ファイルがあれば消す"""
    common.delete_file(FILE_PATH)


def preparation_completed():
    """事前準備が完了しているかどうかを確認"""
    if not (os.path.isfile(FILE_PATH)):
        msg_display.display_err(msg_mod.get('setup_sync', 'not_entered'))
        raise DidNotFinishError


# ----- for cell -----
def display_forms():
    delete_tmp_file()
    initial_experiment()


def create_package():
    try:
        preparation_completed()

        params = get_params()
        experiment_path = p.create_experiments_with_subpath(params[KEY_EX_PKG])
        # create experimental package
        ex_pkg.create_ex_package(dmp.get_datasetStructure(), experiment_path)
        # create parameter folder
        parama_ex_name = params[KEY_EX_PARAM]
        if len(parama_ex_name) > 0:
            shutil.move(os.path.join(experiment_path, 'parameter'), os.path.join(experiment_path, parama_ex_name))
        # create ci folder
        if params[KEY_CREATE_CI]:
            path = os.path.join(experiment_path, 'ci')
            os.makedirs(path, exist_ok=True)
            Path(os.path.join(path, '.gitkeep')).touch(exist_ok=True)
        # create test folder
        if params[KEY_CREATE_TEST]:
            path = os.path.join(experiment_path, 'source', 'test')
            os.makedirs(path, exist_ok=True)
            Path(os.path.join(path, '.gitkeep')).touch(exist_ok=True)

        ex_pkg_info.set_current_experiment_title(params['ex_pkg_name'])

    except Exception:
        msg_display.display_err(msg_mod.get('ex_setup', 'create_pkg_error'))
        raise
    else:
        msg_display.display_info(msg_mod.get('ex_setup', 'create_pkg_success'))


def del_build_token():
    """不要なGIN-forkトークンの削除"""
    preparation_completed()
    url = git_module.get_remote_url()

    try:
        # delete build token(only private)
        token.del_build_token_by_remote_origin_url(url)
    except requests.exceptions.RequestException:
        msg_display.display_err(msg_mod.get('build_token', 'connection_error'))
        raise
    except Exception:
        raise


def datalad_create():
    """ローカルをdataladデータセット化する"""
    preparation_completed()
    sync.datalad_create(p.HOME_PATH)


def ssh_create_key():
    """SSH keyの作成"""
    preparation_completed()
    ssh.create_key()


def upload_ssh_key():
    """GIN-frokへ公開鍵の登録"""
    preparation_completed()
    ssh.upload_ssh_key()


def ssh_trust_gin():
    """SSHホスト（=GIN）を信頼する設定"""
    preparation_completed()
    ssh.trust_gin()


def prepare_sync():
    """同期するコンテンツの制限"""
    preparation_completed()
    sync.prepare_sync()


def setup_sibling():
    """siblingを設定する"""
    preparation_completed()
    sync.setup_sibling()


def add_container():
    """GIN-forkの実行環境一覧へ追加"""
    preparation_completed()
    container.add_container(ex_pkg_info.exec_get_ex_title())


def finished_setup():
    """実験フローの『初期セットアップ』に済を付与する。"""
    preparation_completed()
    flow.put_mark_experiment()


def syncs_config() -> tuple[list[str], list[str], list[str], str]:
    """同期のためにファイルとメッセージの設定"""
    preparation_completed()
    # get experiment title
    experiment_title = ex_pkg_info.exec_get_ex_title()
    # set sync path
    git_path, gitannex_path, gitannex_files = ex_pkg.create_syncs_path(p.create_experiments_with_subpath(experiment_title))
    nb_path = os.path.join(p.EXP_DIR_PATH, 'required_every_time.ipynb')
    git_path.append(nb_path)
    # set commit message
    commit_message = msg_mod.get('commit_message', 'required_every_time').format(experiment_title)
    # delete temporarily file
    delete_tmp_file()
    return git_path, gitannex_path, gitannex_files, commit_message


# ----- utils -----
def submit_init_experiment_callback(input_forms, input_radios, error_message, submit_button):
    """Processing method after click on submit button"""
    def callback(event):
        delete_tmp_file()
        user_name = input_forms[0].value
        password = input_forms[1].value
        package_name = input_forms[2].value
        paramfolder_name = None
        if len(input_forms) > 3:
            paramfolder_name = input_forms[3].value
        is_test_folder = False
        is_ci_folder = False
        if input_radios[0].value ==  msg_mod.get('setup_package','true'):
            is_test_folder = True
        if input_radios[1].value ==  msg_mod.get('setup_package','true'):
            is_ci_folder = True

        # validate value for forms
        if not pre.validate_user_auth(user_name, password, submit_button):
            return

        if not pre.validate_experiment_folder_name(package_name, p.create_experiments_with_subpath(package_name), msg_mod.get('setup_package','package_name_title'), submit_button):
            return

        if paramfolder_name is not None:
            if not pre.validate_parameter_folder_name(paramfolder_name, package_name, submit_button):
                return

        try:
            pre.setup_local(user_name, password)
            if paramfolder_name is None:
                paramfolder_name = ""
            set_params(package_name, paramfolder_name, is_test_folder, is_ci_folder)

        except Unauthorized:
            submit_button.button_type = 'warning'
            submit_button.name =  msg_mod.get('user_auth','unauthorized')
            return
        except requests.exceptions.RequestException as e:
            submit_button.button_type = 'danger'
            submit_button.name =  msg_mod.get('DEFAULT','connection_error')
            error_message.value = 'ERROR : {}'.format(traceback.format_exception_only(type(e), e)[0].rstrip('\\n'))
            error_message.object = pn.pane.HTML(error_message.value)
            return
        except Exception as e:
            submit_button.button_type = 'danger'
            submit_button.name =  msg_mod.get('DEFAULT','unexpected')
            error_message.value = 'ERROR : {}'.format(traceback.format_exception_only(type(e), e)[0].rstrip('\\n'))
            error_message.object = pn.pane.HTML(error_message.value)
            return
        else:
            submit_button.button_type = 'success'
            submit_button.name =  msg_mod.get('setup_package','success')
            return
    return callback


def initial_experiment():
    pn.extension()

    # form of user name and password
    input_forms = pre.create_user_auth_forms()

    # form of experiment
    package_name_form = pn.widgets.TextInput(name=msg_mod.get('setup_package','package_name_title'), placeholder=msg_mod.get('setup_package','package_name_help'), width=pre.DEFAULT_WIDTH)
    input_forms.append(package_name_form)

    if dmp.is_for_parameter(dmp.get_datasetStructure()):
        paramfolder_form = pre.create_param_form()
        input_forms.append(paramfolder_form)

    options = [msg_mod.get('setup_package','true'),  msg_mod.get('setup_package','false')]
    test_folder_radio = pn.widgets.RadioBoxGroup(options=options, inline=True, value=msg_mod.get('setup_package','true'))
    ci_folder_radio = pn.widgets.RadioBoxGroup(options=options, inline=True, value=msg_mod.get('setup_package','false'))
    input_radios = [test_folder_radio, ci_folder_radio]

    title_format = """<label>{}</label>"""
    test_title = pn.pane.HTML(title_format.format(msg_mod.get('setup_package','test_folder_title')))
    ci_title = pn.pane.HTML(title_format.format(msg_mod.get('setup_package','ci_folder_title')))
    test_column = pn.Column(test_title, test_folder_radio, margin=(0, 0, 0, 5))
    ci_column = pn.Column(ci_title, ci_folder_radio, margin=(0, 0, 0, 5))

    # Instance for exception messages
    error_message = pre.layout_error_text()

    button = pre.create_button(name=msg_mod.get('DEFAULT','end_input'))

    # Define processing after clicking the submit button
    button.on_click(submit_init_experiment_callback(input_forms, input_radios, error_message, button))

    clear_output()
    # Columnを利用すると値を取れない場合がある
    for form in input_forms:
        display(form)
    display(pn.Column(test_column, ci_column))
    display(button)
    display(error_message)
