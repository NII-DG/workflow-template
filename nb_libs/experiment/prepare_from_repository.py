'''prepare_from_repository.ipynbから呼び出されるモジュール'''
import os, json, shutil, git, glob
from json.decoder import JSONDecodeError
from ipywidgets import Text, Button, Layout
from IPython.display import display, clear_output, Javascript
import panel as pn
from datalad import api as datalad_api
from urllib import parse
from http import HTTPStatus
from ..utils.git import annex_util, git_module
from ..utils.path import path, validate
from ..utils.message import message, display as display_util
from ..utils.gin import sync
from ..utils.gin import api as gin_api
from ..utils.common import common
from ..utils.except_class import DidNotFinishError, UnexpectedError
from ..utils.params import param_json


# 辞書のキー
# PATH_TO_URL = 'path_to_url'

# PREFIX = 'prefix'
# PATHS = 'paths'
# SELECTED_PATHS = 'selected_paths'
# LOCATION_CONSTRAINT = 'LocationConstraint'
# CONTENTS = 'Contents'
# KEY = 'Key'
GINFORK_TOKEN = 'ginfork_token'
DATASET_STRUCTURE = "datasetStructure"
REPO_NAME = 'repo_name'
PRIVATE = 'private'
SSH_URL = 'ssh_url'
HTML_URL = 'html_url'
DATASET_STRUCTURE_TYPE = "dataset_structure"
EX_PKG_INFO = 'ex_pkg_info'
EX_PKG_NAME = 'ex_pkg_name'
PARAM_EX_NAME = 'param_ex_name'


# リポジトリのURLを入力するフォームを表示する
def input_repository():


    def on_click_callback(clicked_button: Button) -> None:
        common.delete_file(path.FROM_REPO_JSON_PATH)

        clone_url = text.value
        repo_name = clone_url.split('/')[-1].replace('.git', '')
        repo_owner = clone_url.split('/')[-2]
        with open (path.TOKEN_JSON_PATH, 'r') as f:
            token = json.load(f)[GINFORK_TOKEN]

#         pr = parse.urlparse(param_json.get_gin_http())
        pr = parse.urlparse("https://it1.dg.nii.ac.jp")

        response = gin_api.get_repo_info(pr.scheme, pr.netloc, repo_owner, repo_name, token)

        if response.status_code == HTTPStatus.OK:
            pass

        elif response.status_code == HTTPStatus.NOT_FOUND:
            pass

        else:
            pass

        repo_info = response.json()

        if repo_info[PRIVATE] == True:
            return

        os.makedirs(path.TMP_DIR, exist_ok=True)

        if os.path.exists(path.GET_REPO_PATH):
            shutil.rmtree(path.GET_REPO_PATH)
        os.mkdir(path.GET_REPO_PATH)

        get_repo_name_path = os.path.join(path.GET_REPO_PATH, repo_name)

        git.Repo.clone_from(
            url=clone_url,
            to_path=get_repo_name_path,
            multi_options=['-b master', '--depth 1', '--filter=blob:none']
        )

        # ここでannexブランチをフェッチ
        # git fetch origin git-annex:remotes/origin/git-annex


        try:
            with open(os.path.join(get_repo_name_path, 'dmp.json'), 'r') as f:
                dataset_structure = json.load(f)[DATASET_STRUCTURE]
        except (FileNotFoundError, JSONDecodeError, KeyError):
            shutil.rmtree(path.GET_REPO_PATH)
            return

        get_repo_experiments_path = os.path.join(get_repo_name_path, 'experiments')

        ex_pkg_list = list()
        for data_name in os.listdir(get_repo_experiments_path):
            data_path = os.path.join(get_repo_experiments_path, data_name)
            if os.path.isdir(data_path):
                ex_pkg_list.append(data_name)
        if len(ex_pkg_list) == 0:
            shutil.rmtree(path.GET_REPO_PATH)
            return

        ex_pkg_info_dict = dict()

        for ex_pkg in ex_pkg_list:
            parameter_dirs = glob.glob(os.path.join(get_repo_experiments_path, ex_pkg, '*/output_data/'))
            parameter_dirs = [dir.replace('/output_data/', '') for dir in parameter_dirs]
            parameter_dirs = [dir.replace(os.path.join(get_repo_experiments_path, ex_pkg, ''), '') for dir in parameter_dirs]
            ex_pkg_info_dict[ex_pkg] = parameter_dirs

        from_repo_dict = {
            REPO_NAME: repo_name,
            PRIVATE: repo_info[PRIVATE],
            SSH_URL: repo_info[SSH_URL],
            HTML_URL: repo_info[HTML_URL],
            DATASET_STRUCTURE_TYPE: dataset_structure,
            EX_PKG_INFO: ex_pkg_info_dict
        }

        with open(path.FROM_REPO_JSON_PATH, 'w') as f:
            json.dump(from_repo_dict, f, indent=4)


        clear_output()
        display_util.display_info("入力完了しました")
        display_util.display_msg('URL: '+ clone_url)


    common.delete_file(path.FROM_REPO_JSON_PATH)

    # リポジトリ名入力フォーム
    text = Text(
        description='URL：',
        placeholder='https://dg.nii.ac.jp/user/repository_title.git',
        layout=Layout(width='500px')
    )
    button = Button(description='入力完了')
    button.on_click(on_click_callback)
    display_util.display_info("URLを入力してください。<br>入力完了後、「入力完了」ボタンを押下してください。")
    display(text, button)



def choose_get_data():
    '''取得するデータを選択する
    '''


    def update_second_choices(event):
        selected_value = event.new
        second_choice.options = second_choices_dict[selected_value]
        second_choice.value = second_choices_dict[selected_value][0]


    with open(path.FROM_REPO_JSON_PATH, 'r') as f:
        from_repo_dict = json.load(f)
    if not {REPO_NAME, PRIVATE, SSH_URL, HTML_URL, DATASET_STRUCTURE_TYPE, EX_PKG_INFO}.issubset(set(from_repo_dict.keys())):
        return

    pn.extension()

    first_choices = ['--']
    second_choices_dict = {'--' : ['--']}

    for ex_pkg, ex_param in from_repo_dict[EX_PKG_INFO].items():
        first_choices.append(ex_pkg)
        second_choices_dict[ex_pkg] = ex_param

    if from_repo_dict[DATASET_STRUCTURE_TYPE] == 'with_code':
        first_choice = pn.widgets.Select(name='実験パッケージ名：', options=first_choices)
        display(first_choice)
        button = pn.widgets.Button(name= '選択確定', button_type= "primary", width=700)
        button.on_click(choose_get_data_callback(first_choice, "", button))

    elif from_repo_dict[DATASET_STRUCTURE_TYPE] == 'for_parameter':

        first_choice = pn.widgets.Select(name='実験パッケージ名：', options=first_choices)
        second_choice = pn.widgets.Select(name='パラメータ実験名：', options=second_choices_dict[first_choices[0]])
        display(first_choice)
        display(second_choice)
        button = pn.widgets.Button(name= '選択確定', button_type= "primary", width=700)
        button.on_click(choose_get_data_callback(first_choice, second_choice, button))
        first_choice.param.watch(update_second_choices, 'value')

    display(button)


def choose_get_data_callback(first_choice, second_choice, button):
    """Processing method after click on submit button

    Check form values, authenticate users, and update RF configuration files.

    Args:
        user_auth_forms ([list(TextInput or PasswordInput)]) : [form instance]
        error_message ([StaticText]) : [exception messages instance]
        submit_button_user_auth ([Button]): [Submit button instance]
    """
    def callback(event):

        button.button_type = 'success'

        with open(path.FROM_REPO_JSON_PATH, 'r') as f:
            from_repo_dict = json.load(f)

        from_repo_dict[EX_PKG_NAME] = first_choice.value
        from_repo_dict[PARAM_EX_NAME] = second_choice.value

        with open(path.FROM_REPO_JSON_PATH, 'w') as f:
            json.dump(from_repo_dict, f, indent=4)
        return

    return callback










# def prepare_addurls_data():
#     """リポジトリへのリンク登録のためのcsvファイルを作成する

#     Exception:
#         DidNotFinishError: .tmp内のファイルが存在しない場合
#         KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
#     """
#     try:
#         with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
#             dic = json.load(f)
#             input_url = dic[S3_OBJECT_URL]
#             dest_file_path = dic[DEST_FILE_PATH]
#     except FileNotFoundError as e:
#         display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
#         raise DidNotFinishError() from e
#     except (KeyError, JSONDecodeError):
#         display_util.display_err(message.get('from_repo_s3', 'unexpected'))
#         raise
#     else:
#         annex_util.create_csv({dest_file_path: input_url})


# def add_url():
#     """リポジトリに取得データのS3オブジェクトURLと格納先パスを登録する

#     Exception:
#         DidNotFinishError: .tmp内のファイルが存在しない場合
#         AddurlsError: addurlsに失敗した場合
#     """
#     annex_util.addurl()
#     display_util.display_info(message.get('from_repo_s3', 'create_link_success'))


# def save_annex():
#     """データ取得履歴を記録する

#     Exception:
#         DidNotFinishError: .tmp内のファイルが存在しない場合
#         KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
#         UnexpectedError: 想定外のエラーが発生した場合
#     """
#     try:
#         with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
#             dest_file_path = json.load(f)[DEST_FILE_PATH]
#         # The data stored in the source folder is managed by git, but once committed in git annex to preserve the history.
#         # *No metadata is assigned to the annexed file because the actual data has not yet been acquired.
#         annex_file_paths = [dest_file_path]
#         git_module.git_annex_lock(path.HOME_PATH)
#         sync.save_annex_and_register_metadata(gitannex_path=annex_file_paths, gitannex_files=[], message=message.get('from_repo_s3', 'data_from_s3'))
#     except FileNotFoundError as e:
#         display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
#         raise DidNotFinishError() from e
#     except (KeyError, JSONDecodeError):
#         display_util.display_err(message.get('from_repo_s3', 'unexpected'))
#         raise
#     except Exception as e:
#         display_util.display_err(message.get('from_repo_s3', 'process_fail'))
#         raise UnexpectedError() from e
#     else:
#         clear_output()
#         display_util.display_info(message.get('from_repo_s3', 'process_success'))


# def get_data():
#     """取得データの実データをダウンロードする

#     Exception:
#         DidNotFinishError: .tmp内のファイルが存在しない場合
#         KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
#         UnexpectedError: 想定外のエラーが発生した場合
#     """
#     try:
#         # The data stored in the source folder is managed by git, but once committed in git annex to preserve the history.
#         # *No metadata is assigned to the annexed file because the actual data has not yet been acquired.
#         with open(path.PKG_INFO_JSON_PATH, mode='r') as f:
#             experiment_title = json.load(f)[EX_PKG_NAME]
#         with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
#             dest_file_path = json.load(f)[DEST_FILE_PATH]

#         annex_file_paths = [dest_file_path]
#         # Obtain the actual data of the created link.
#         api.get(path=annex_file_paths)
#         annex_util.annex_to_git(annex_file_paths, experiment_title)
#     except FileNotFoundError as e:
#         display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
#         raise DidNotFinishError() from e
#     except (KeyError, JSONDecodeError):
#         display_util.display_err(message.get('from_repo_s3', 'unexpected'))
#         raise
#     except Exception as e:
#         display_util.display_err(message.get('from_repo_s3', 'process_fail'))
#         raise UnexpectedError() from e
#     else:
#         clear_output()
#         display_util.display_info(message.get('from_repo_s3', 'download_success'))


# def prepare_sync() -> dict:
#     """同期の準備を行う

#     Returns:
#         dict: syncs_with_repoの引数が入った辞書
#     Exception:
#         DidNotFinishError: jsonファイルの形式が想定通りでない場合
#         KeyError, JSONDecodeError: .tmp内のjsonファイルの形式が不正な場合
#     """

#     display(Javascript('IPython.notebook.save_checkpoint();'))

#     git_file_paths = []
#     try:
#         with open(path.PKG_INFO_JSON_PATH, mode='r') as f:
#             experiment_title = json.load(f)[EX_PKG_NAME]
#         with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
#             dest_file_path = json.load(f)[DEST_FILE_PATH]
#     except FileNotFoundError as e:
#         display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
#         raise DidNotFinishError() from e
#     except (KeyError, JSONDecodeError):
#         display_util.display_err(message.get('from_repo_s3', 'unexpected'))
#         raise

#     annex_file_paths = [dest_file_path]

#     if dest_file_path.startswith(path.create_experiments_with_subpath(experiment_title, 'source/')):
#         git_file_paths.append(dest_file_path)

#     annex_file_paths = list(set(annex_file_paths) - set(git_file_paths))
#     git_file_paths.append(path.EXP_DIR_PATH + path.PREPARE_UNIT_FROM_S3)

#     sync_repo_args = dict()
#     sync_repo_args['git_path'] = git_file_paths
#     sync_repo_args['gitannex_path'] = annex_file_paths
#     sync_repo_args['gitannex_files'] = annex_file_paths
#     sync_repo_args['get_paths'] = [path.create_experiments_with_subpath(experiment_title)]
#     sync_repo_args['message'] = message.get('from_repo_s3', 'prepare_data').format(experiment_title)

#     common.delete_file(path.UNIT_S3_JSON_PATH)
#     common.delete_file(path.ADDURLS_CSV_PATH)

#     return sync_repo_args