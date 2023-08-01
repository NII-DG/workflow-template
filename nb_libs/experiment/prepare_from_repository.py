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
from ..utils.params import token, param_json, ex_pkg_info


# 辞書のキー
# PREFIX = 'prefix'
# PATHS = 'paths'
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
SELECTED_DATA = 'selected_data'
INPUT_DATA = 'input_data'
SOURCE = 'source'
OUTPUT_DATA = 'output_data'
PATH_TO_URL = 'path_to_url'


def input_repository():
    '''リポジトリのURLを入力するフォームを表示する
    '''


    def on_click_callback(clicked_button: Button) -> None:
        common.delete_file(path.FROM_REPO_JSON_PATH)

        clone_url = text.value

        # 空文字でないこと
        if clone_url == '':
            button.name = message.get('from_repo_s3', 'empty_url')
            button.button_type = 'danger'
            return

        pr = parse.urlparse(clone_url)

        # 先頭の'/'と'.git'を削除してから'/'で分割
        repo_owner_and_name = pr.path[1:].replace('.git', '').split('/')

        # 要素が2つであること
        if len(repo_owner_and_name) != 2:
            button.name = str()
            return

        repo_owner, repo_name = repo_owner_and_name
        ginfork_token = token.get_ginfork_token()
        gin_pr = parse.urlparse(param_json.get_gin_http())
        response = gin_api.get_repo_info(gin_pr.scheme, gin_pr.netloc, repo_owner, repo_name, ginfork_token)

        # GIN-forkに存在するリポジトリであること
        if response.status_code == HTTPStatus.OK:
            pass

        elif response.status_code == HTTPStatus.NOT_FOUND:
            pass

        else:
            pass

        repo_info = response.json()


        # 公開リポジトリであること
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

        # annexブランチをフェッチ
        os.chdir(get_repo_name_path)
        repo = git.Repo(get_repo_name_path)
        repo.git.fetch('origin', 'git-annex:remotes/origin/git-annex')
        os.chdir(os.environ['HOME'])

        # dmp.jsonが存在すること
        try:
            with open(os.path.join(get_repo_name_path, 'dmp.json'), 'r') as f:
                dataset_structure = json.load(f)[DATASET_STRUCTURE]
        except (FileNotFoundError, JSONDecodeError, KeyError):
            shutil.rmtree(path.GET_REPO_PATH)
            return

        get_repo_experiments_path = os.path.join(get_repo_name_path, 'experiments')

        ex_pkg_list = list()
        for data_name in os.listdir(get_repo_experiments_path):
            if os.path.isdir(os.path.join(get_repo_experiments_path, data_name)):
                ex_pkg_list.append(data_name)

        # 実験パッケージが存在すること
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

        os.makedirs(path.RF_FORM_DATA_DIR, exist_ok=True)
        with open(path.FROM_REPO_JSON_PATH, 'w') as f:
            json.dump(from_repo_dict, f, indent=4)


        button.name = "入力完了しました"
        button.button_type = 'success'

    pn.extension()
    common.delete_file(path.FROM_REPO_JSON_PATH)

    # リポジトリ名入力フォーム
    text = Text(
        description='URL：',
        placeholder='Enter name of repository URL here…',
        layout=Layout(width='500px'),
        style = {'description_width': 'initial'}
    )
    button = pn.widgets.Button(name= '入力完了', button_type= "primary", width=300)
    button.on_click(on_click_callback)
    display_util.display_info("URLを入力してください。<br>入力完了後、「入力完了」ボタンを押下してください。")
    display(text, button)



def choose_get_pkg():
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
        button = pn.widgets.Button(name= '選択確定', button_type= "primary", width=300)
        button.on_click(choose_get_pkg_callback(first_choice, None, button))
        display(first_choice)
        display(button)

    elif from_repo_dict[DATASET_STRUCTURE_TYPE] == 'for_parameters':
        first_choice = pn.widgets.Select(name='実験パッケージ名：', options=first_choices)
        second_choice = pn.widgets.Select(name='パラメータ実験名：', options=second_choices_dict[first_choices[0]])
        button = pn.widgets.Button(name= '選択確定', button_type= "primary", width=300)
        button.on_click(choose_get_pkg_callback(first_choice, second_choice, button))
        first_choice.param.watch(update_second_choices, 'value')
        display(first_choice)
        display(second_choice)
        display(button)

    else:
        raise Exception('---------------------------------------------------------')


def choose_get_pkg_callback(first_choice, second_choice, button):
    """Processing method after click on submit button

    Check form values, authenticate users, and update RF configuration files.

    Args:
        user_auth_forms ([list(TextInput or PasswordInput)]) : [form instance]
        error_message ([StaticText]) : [exception messages instance]
        submit_button_user_auth ([Button]): [Submit button instance]
    """
    def callback(event):


        with open(path.FROM_REPO_JSON_PATH, 'r') as f:
            from_repo_dict = json.load(f)

        from_repo_dict[EX_PKG_NAME] = first_choice.value
        repo_name = from_repo_dict[REPO_NAME]

        if second_choice is None:
            from_repo_dict[PARAM_EX_NAME] = ''
            pkg_path = os.path.join(path.GET_REPO_PATH, repo_name, 'experiments', first_choice.value)
        else:
            from_repo_dict[PARAM_EX_NAME] = second_choice.value
            pkg_path = os.path.join(path.GET_REPO_PATH, repo_name, 'experiments', first_choice.value, second_choice.value)

        if not os.path.isdir(pkg_path):
            button.button_type = 'danger'
            button.name = pkg_path
            return

        with open(path.FROM_REPO_JSON_PATH, 'w') as f:
            json.dump(from_repo_dict, f, indent=4)

        button.button_type = 'success'
        button.name = '選択完了'
        return


    return callback




def choose_get_data():

    with open(path.FROM_REPO_JSON_PATH, 'r') as f:
        from_repo_dict = json.load(f)
    if not {EX_PKG_NAME, PARAM_EX_NAME}.issubset(set(from_repo_dict.keys())):
        return

    repo_name = from_repo_dict[REPO_NAME]
    package = from_repo_dict[EX_PKG_NAME]
    parameter = from_repo_dict[PARAM_EX_NAME]

    package_path = os.path.join(path.GET_REPO_PATH, repo_name, 'experiments', package)

    def gen_gui_list(event):




        # for i in range(len(column)):
        #     if len(column[i].value) > 0:
        #         gui_list.append('### ' + column[i].name)

        #     for index in range(len(column[i].value)):
        #         gui_list.append(pn.widgets.TextInput(name=column[i].name + '/' + column[i].value[index], placeholder='Enter a file path here...', width=700))


        # リポジトリ名/ 以降の相対パスを格納する
        selected_data_dict = dict()
        selected_data_count = 0
        for column in columns:
            if 'MultiSelect' in str(type(column)):
                selected_data_dict[column.name] = list()
                for file_path in column.value:
                    selected_data_dict[column.name].append(os.path.join('experiments', package, column.name, file_path))
                    selected_data_count += 1

        # データが選択されていない場合
        if selected_data_count == 0:
            done_button.button_type = "danger"
            return

        from_repo_dict[SELECTED_DATA] = selected_data_dict
        with open(path.FROM_REPO_JSON_PATH, 'w') as f:
            json.dump(from_repo_dict, f, indent=4)

        done_button.button_type = "success"
        done_button.name = "選択完了しました。次の処理にお進みください。"

    done_button = pn.widgets.Button(name= "選択を完了する", button_type= "primary")
    done_button.on_click(gen_gui_list)

    # Create a list of files for each input_data, source, and output_data folder.
    def get_files(target, parameter) -> list:
        if parameter == '':
            cmd_glob = os.path.join(package_path, target, '**')
            cmd_replace = os.path.join(package_path, target, '')
        else:
            cmd_glob = os.path.join(package_path, parameter, target, '**')
            cmd_replace = os.path.join(package_path, parameter, target, '')
        files = glob.glob(cmd_glob, recursive=True)
        files = common.sortFilePath(files)
        files = [file.replace(cmd_replace, '') for file in files if not os.path.isdir(file) ]
        return files

    # For each input_data, source, and output_data folder, create a MultiSelect screen to select the data to be retrieved and return a list of GUIs.
    def generate_gui(files_list:dict) -> list:
        gui_list = []
        for key, value in files_list.items():
            if key == 'input_data' or  key == 'source':
                gui_list.append(pn.widgets.MultiSelect(name=key, options=value, size=8, sizing_mode='stretch_width'))
            elif key == 'output_data':
                gui_list.append(pn.widgets.MultiSelect(name=os.path.join(parameter, key), options=value, size=8, sizing_mode='stretch_width'))
        return gui_list

    # Generate a GUI that matches the configuration of the experimental package.
    input_data_files = get_files(target='input_data', parameter='')
    source_files = get_files(target='source', parameter='')
    output_data_files = get_files(target='output_data', parameter=parameter)
    files_list = {"input_data":input_data_files, "source":source_files, "output_data":output_data_files}
    gui = generate_gui(files_list)

    # Display GUI.
    pn.extension()
    columns = pn.Column()
    for target in gui:
        columns.append(target)
    columns.append(done_button)
    display(columns)





def input_path():
    '''データの格納先を入力するフォームを出力する

    Exception:
        JSONDecodeError: jsonファイルの形式が想定通りでない場合
    '''
    def verify_input_text(event):
        '''入力された格納先を検証しファイルに記録する
        '''

        input_path_and_from_list = [(column.value_input, column.name) for column in columns if 'TextInput' in str(type(column))]
        experiment_title = ex_pkg_info.get_current_experiment_title()

        # 格納先パスの検証
        err_msg = validate.validate_input_path(input_path_and_from_list, experiment_title)
        if len(err_msg) > 0:
            done_button.button_type = "danger"
            done_button.name = err_msg
            return


        repo_name = from_repo_dict[REPO_NAME]
        path_to_url_dict = dict()
        repo_path = os.path.join(path.GET_REPO_PATH, repo_name)

        done_button.name = repo_path

        for input_path, input_from in input_path_and_from_list:

            result = git_module.git_annex_whereis(os.path.join(repo_path, input_from), repo_path)
            done_button.name = result
            if 'URL' in result:
                data = json.loads(result)
                input_url = data['key'].replace(' ', '%20')

            else:
                html_url = from_repo_dict[HTML_URL]
                ex_pkg_name = from_repo_dict[EX_PKG_NAME]
                input_url = os.path.join(html_url, 'raw', 'master', 'experiments', ex_pkg_name, input_from).replace(' ', '%20')

            ex_pkg_name = from_repo_dict[EX_PKG_NAME]

            input_path = os.path.join(repo_path, 'experiments', ex_pkg_name, input_path)
            path_to_url_dict[input_path] = input_url

        from_repo_dict[PATH_TO_URL] = path_to_url_dict
        with open(path.FROM_REPO_JSON_PATH, mode='w') as f:
            json.dump(from_repo_dict, f, indent=4)

        done_button.button_type = "success"
        done_button.name = message.get('from_repo_s3', 'done_input')


    with open(path.FROM_REPO_JSON_PATH, 'r') as f:
        from_repo_dict:dict = json.load(f)
    if not SELECTED_DATA in from_repo_dict.keys():
        raise Exception('------------------------------------------------------')

    selected_data = from_repo_dict[SELECTED_DATA]

    # 入力フォーム表示
    pn.extension()
    columns = pn.Column()
    for k, v in selected_data.items():
        columns.append('### ' + k)
        for selected_path in v:
            columns.append(pn.widgets.TextInput(name=selected_path, placeholder=message.get('from_repo_s3', 'enter_a_file_path'), width=700))
    done_button = pn.widgets.Button(name= message.get('from_repo_s3', 'end_input'), button_type= "primary")
    columns.append(done_button)
    done_button.on_click(verify_input_text)
    display(columns)





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


# def get_pkg():
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
