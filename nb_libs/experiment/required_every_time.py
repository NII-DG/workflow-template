import os
import json
import requests
import traceback
import panel as pn
from IPython.display import clear_output, display
from ..utils.common import common
from ..utils.form import prepare as pre
from ..utils.message import message as msg_mod, display as msg_display
from ..utils.params import ex_pkg_info, token
from ..utils.git import git_module
from ..utils.gin import sync, ssh, container
from ..utils.path import path as p
from ..utils.flow import module as flow
from ..utils.except_class import DidNotFinishError, Unauthorized, DGTaskError


FILE_PATH = os.path.join(p.RF_FORM_DATA_DIR, 'required_every_time.json')


# tmp_file handling
def set_params(ex_pkg_name:str, parama_ex_name:str, create_test_folder:bool, create_ci:bool):
    params_dict = {
    "ex_pkg_name" : ex_pkg_name,
    "parama_ex_name" : parama_ex_name,
    "create_test_folder" : create_test_folder,
    "create_ci" : create_ci
    }
    with open(FILE_PATH, 'w') as f:
        json.dump(params_dict, f, indent=4)


def get_param():
    with open(FILE_PATH, mode='r') as f:
            params = json.load(f)
    return params


def delete_tmp_file():
    """ファイルがあれば消す"""
    common.delete_file(FILE_PATH)


def preparation_completed():
    if not (os.path.isfile(FILE_PATH)):
        msg_display.display_err(msg_mod.get('setup_sync', 'not_entered'))
        raise DidNotFinishError


# for cell
def display_forms():
    delete_tmp_file()
    initial_experiment()


def create_package():
    preparation_completed()


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
    container.add_container()


def finished_setup():
    """実験フローの『初期セットアップ』に済を付与する。"""
    preparation_completed()
    flow.put_mark_experiment()


def syncs_config() -> tuple[list[str], list[str], list[str], str]:
    """同期のためにファイルとメッセージの設定"""
    preparation_completed()
    experiment_title = ex_pkg_info.get_current_experiment_title()
    if experiment_title is None:
        msg_display.display_err(msg_mod.get('experiment_error', 'experiment_setup_unfinished'))
        raise DGTaskError
    git_path, gitannex_path, gitannex_files = create_syncs_path()
    commit_message = f'{experiment_title}_リサーチフロー実行準備'
    return git_path, gitannex_path, gitannex_files, commit_message


# utils
def create_syncs_path()-> tuple[list[str], list[str], list[str]]:
    os.chdir(experiment_path)

    #**************************************************#
    #* Generate a list of folder paths to be managed by Git-annex. #
    #**************************************************#
    dirlist=[]
    filelist=[]
    annexed_save_path=[]

    # Recursively search under the experimental package to obtain a list of absolute directory paths.
    for root, dirs, files in os.walk(top=experiment_path):
        for dir in dirs:
            dirPath = os.path.join(root, dir)
            dirlist.append( dirPath )

    # Add directory paths containing the string "output_data" that are not included under input_data to annexed_save_path.
    output_data_path = [ s for s in dirlist if 'output_data' in s ]
    for output_data in output_data_path:
        if  "input_data" not in output_data:
            annexed_save_path.append( output_data )

    # Add the input_data directory to annexed_save_path.
    annexed_save_path.append( experiment_path + '/input_data'  )

    # Generate a list of file paths to which metadata is to be assigned.
    gitannex_files = []
    for path in annexed_save_path:
        gitannex_files += [p for p in glob.glob(path+'/**', recursive=True)
                if os.path.isfile(p)]

    #********************************************************#
    #* Generate a list of directory paths and file paths to be managed by Git. #
    #********************************************************#
    # Obtain a list of directories and files directly under the experimental package.
    files = os.listdir()

    # Delete Git-annex managed directories (input_data and output_data) from the retrieved list.
    dirs = [f for f in files if os.path.isdir(f)]

    for dirname in dirs:
        if dirname == 'input_data' :
            dirs.remove('input_data')

        if dirname == 'output_data' :
            dirs.remove('output_data')

    for dirname in dirs:
        if dirname != 'ci' and dirname != 'source':
            full_param_dir = '{}/{}/params'.format(experiment_path,dirname)
            if os.path.isdir(full_param_dir):
                dirs.remove(dirname)
                ex_param_path = '{}/{}'.format(experiment_path, dirname)
                ex_param_path_childs = os.listdir(ex_param_path)
                for ex_param_path_child in ex_param_path_childs:
                    if ex_param_path_child != 'output_data':
                        dirs.append('{}/{}'.format(dirname,ex_param_path_child))

    # Obtain files directly under the experimental package.
    files = [f for f in files if os.path.isfile(f)]

    # Generate a list of folder paths and file paths to be managed by Git.
    files.extend(dirs)
    save_path = []
    for file in files:
        save_path.append(experiment_path + '/' + file)

    return save_path, annexed_save_path, gitannex_files


def submit_init_experiment_callback(input_forms, input_radios, error_message, submit_button):

    def callback(event):
        delete_tmp_file()
        user_name = input_forms[0].value
        password = input_forms[1].value
        package_name = input_forms[2].value
        paramfolder_name = None
        if len(input_forms) > 3:
            paramfolder_name = input_forms[4].value
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
            submit_button.button_type = 'warning'
            submit_button.name =  msg_mod.get('user_auth','connection_error')
            error_message.value = 'ERROR : {}'.format(traceback.format_exception_only(type(e), e)[0].rstrip('\\n'))
            error_message.object = pn.pane.HTML(error_message.value)
            return
        except Exception as e:
            submit_button.button_type = 'danger'
            submit_button.name =  msg_mod.get('user_auth','unexpected')
            error_message.value = 'ERROR : {}'.format(traceback.format_exception_only(type(e), e)[0].rstrip('\\n'))
            error_message.object = pn.pane.HTML(error_message.value)
            return
        else:
            submit_button.button_type = 'success'
            submit_button.name =  msg_mod.get('user_auth','success')
            return
    return callback


def initial_experiment():
    pn.extension()

    # form of user name and password
    input_forms = pre.create_user_auth_forms()

    # form of experiment
    package_name_form = pn.widgets.TextInput(name= msg_mod.get('setup_package','package_name_title'), width=700)
    input_forms.append(package_name_form)

    assigned_values = sync.fetch_gin_monitoring_assigned_values()
    if assigned_values['datasetStructure'] == 'for_parameters':
        paramfolder_form = pre.create_param_forms()
        input_forms.append(paramfolder_form)

    options = [ msg_mod.get('setup_package','true'),  msg_mod.get('setup_package','false')]
    init_value =  msg_mod.get('setup_package','false')
    test_folder_radio = pn.widgets.RadioBoxGroup(name=msg_mod.get('setup_package','test_folder_title'), options=options, inline=True, value=init_value)
    ci_folder_radio = pn.widgets.RadioBoxGroup(name=msg_mod.get('setup_package','ci_folder_title'), options=options, inline=True, value=init_value)
    input_radios = [test_folder_radio, ci_folder_radio]

    # Instance for exception messages
    error_message = pre.layout_error_text()

    button = pn.widgets.Button(name=msg_mod.get('DEFAULT','end_input'), button_type= "primary", width=700)

    # Define processing after clicking the submit button
    button.on_click(submit_init_experiment_callback(input_forms, input_radios, error_message, button))

    clear_output()
    display(pn.Column(*input_forms, *input_radios, button, error_message))