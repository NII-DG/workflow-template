'''prepare_from_repository.ipynbから呼び出されるモジュール'''
import os, json, shutil, git, glob
from json.decoder import JSONDecodeError
from ipywidgets import Text, Button, Layout
from IPython.display import display, clear_output, Javascript
import panel as pn
from datalad import api as datalad_api
from urllib import parse
from http import HTTPStatus
from requests.exceptions import RequestException
from datalad.support.exceptions import IncompleteResultsError
from ..utils.git import annex_util, git_module
from ..utils.path import path, validate
from ..utils.message import message, display as display_util
from ..utils.gin import api as gin_api, sync
from ..utils.common import common
from ..utils.except_class import DidNotFinishError, UnexpectedError
from ..utils.params import token, ex_pkg_info
from ..utils.form import prepare as pre


# 辞書のキー
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
KEY = 'key'
URLS = 'urls'
WHEREIS = 'whereis'


def input_repository():
    '''リポジトリURLを入力する
    '''


    def on_click_callback(clicked_button: Button) -> None:
        '''入力されたURLの検証を行い、ファイルに記録する
        '''

        common.delete_file(path.FROM_REPO_JSON_PATH)

        clone_url = text.value

        # 空文字でないこと
        if clone_url == '':
            button.name = message.get('from_repo_s3', 'empty_url')
            button.button_type = 'danger'
            return

        pr = parse.urlparse(clone_url)

        # 先頭の'/'と'.git'を削除してから'/'で分割
        repo_owner_repo_name = pr.path[1:].replace('.git', '').split('/')

        # 要素が2つであること
        if len(repo_owner_repo_name) != 2:
            button.name = message.get('from_repo_s3', 'invalid_url')
            button.button_type = 'danger'
            return

        repo_owner, repo_name = repo_owner_repo_name
        ginfork_token = token.get_ginfork_token()

        # GIN-forkのapi/v1/reposを呼ぶ
        try:
            response = gin_api.get_repo_info(pr.scheme, pr.netloc, repo_owner, repo_name, ginfork_token)
        except RequestException:
            button.name = message.get('from_repo_s3', 'invalid_url')
            button.button_type = 'danger'
            return

        # GIN-forkに存在するリポジトリであること
        if response.status_code == HTTPStatus.OK:
            pass
        elif response.status_code == HTTPStatus.NOT_FOUND:
            button.name = message.get('from_repo_s3', 'wrong_or_unauthorized')
            button.button_type = 'danger'
            return
        else:
            button.name = message.get('from_repo_s3', 'invalid_url')
            button.button_type = 'danger'
            return

        repo_info = response.json()

        # 公開リポジトリであること
        if repo_info[PRIVATE] == True:
            button.name = message.get('from_repo_s3', 'private_repo')
            button.button_type = 'danger'
            return

        #.tmp, .tmp/get_repoを作成
        os.makedirs(path.TMP_DIR, exist_ok=True)
        if os.path.isdir(path.GET_REPO_PATH):
            shutil.rmtree(path.GET_REPO_PATH)
        os.mkdir(path.GET_REPO_PATH)

        # get_repo/:repo_nameの絶対パス
        repository_path = os.path.join(path.GET_REPO_PATH, repo_name)

        git.Repo.clone_from(
            url=clone_url,
            to_path=repository_path,
            multi_options=['-b master', '--depth 1', '--filter=blob:none']
        )

        # annexブランチをフェッチ
        try:
            os.chdir(repository_path)
            repo = git.Repo(repository_path)
            repo.git.fetch('origin', 'git-annex:remotes/origin/git-annex')
        except Exception as e:
            error_message.value = str(e)
            button.button_type = 'danger'
            return
        finally:
            os.chdir(path.HOME_PATH)

        # dmp.jsonが存在すること
        try:
            with open(os.path.join(repository_path, 'dmp.json'), 'r') as f:
                dataset_structure = json.load(f)[DATASET_STRUCTURE]
        except (FileNotFoundError, JSONDecodeError, KeyError):
            button.name = message.get('from_repo_s3', 'invalid_repo')
            button.button_type = 'danger'
            if os.path.isdir(repository_path):
                shutil.rmtree(repository_path)
            return

        experiments_path = os.path.join(repository_path, 'experiments')

        ex_pkg_list = list()
        for ex_pkg in os.listdir(experiments_path):
            if os.path.isdir(os.path.join(experiments_path, ex_pkg)):
                ex_pkg_list.append(ex_pkg)

        # 実験パッケージが存在すること
        if len(ex_pkg_list) == 0:
            button.name = message.get('from_repo_s3', 'invalid_repo')
            button.button_type = 'danger'
            if os.path.isdir(repository_path):
                shutil.rmtree(repository_path)
            return

        ex_pkg_info_dict = dict()

        # パラメータ実験名を取得
        for ex_pkg in ex_pkg_list:
            parameter_dirs = glob.glob(os.path.join(experiments_path, ex_pkg, '*/output_data/'))
            parameter_dirs = [dir.replace('/output_data/', '') for dir in parameter_dirs]
            parameter_dirs = [dir.replace(os.path.join(experiments_path, ex_pkg, ''), '') for dir in parameter_dirs]
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

        button.name = message.get('from_repo_s3', 'done_input')
        button.button_type = 'success'


    common.delete_file(path.FROM_REPO_JSON_PATH)
    pn.extension()

    # 入力フォームを表示
    text = Text(
        description=message.get('from_repo_s3', 'url'),
        placeholder=message.get('from_repo_s3', 'enter_repo_url'),
        layout=Layout(width='500px'),
        style = {'description_width': 'initial'}
    )
    button = pn.widgets.Button(name= message.get('from_repo_s3', 'end_input'), button_type= "primary", width=300)
    button.on_click(on_click_callback)
    error_message = pre.layout_error_text()
    display(text, button, error_message)


def choose_get_pkg():
    '''取得するデータを選択する
    '''


    def update_second_choices(event):
        '''実験パッケージ名が選択された際にパラメータ実験名の選択肢を更新する
        '''
        selected_value = event.new
        ex_param_choice.options = ex_param_choices_dict[selected_value]
        ex_param_choice.value = ex_param_choices_dict[selected_value][0]


    try:
        with open(path.FROM_REPO_JSON_PATH, 'r') as f:
            from_repo_dict:dict = json.load(f)
    except FileNotFoundError:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        return

    # 辞書のキーが存在すること
    if not {REPO_NAME, PRIVATE, SSH_URL, HTML_URL, DATASET_STRUCTURE_TYPE, EX_PKG_INFO}.issubset(set(from_repo_dict.keys())):
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        return

    ex_pkg_choices = ['--']
    ex_param_choices_dict = {'--' : ['--']}

    for ex_pkg, ex_param in from_repo_dict[EX_PKG_INFO].items():
        ex_pkg_choices.append(ex_pkg)
        ex_param_choices_dict[ex_pkg] = ex_param

    # 入力フォームを表示
    pn.extension()

    if from_repo_dict[DATASET_STRUCTURE_TYPE] == 'with_code':
        ex_pkg_choice = pn.widgets.Select(name=message.get('from_repo_s3', 'ex_pkg_name'), options=ex_pkg_choices)
        button = pn.widgets.Button(name= message.get('from_repo_s3', 'end_choose'), button_type= "primary", width=300)
        button.on_click(choose_get_pkg_callback(ex_pkg_choice, None, button, from_repo_dict))
        display(ex_pkg_choice)
        display(button)

    elif from_repo_dict[DATASET_STRUCTURE_TYPE] == 'for_parameters':
        ex_pkg_choice = pn.widgets.Select(name=message.get('from_repo_s3', 'ex_pkg_name'), options=ex_pkg_choices)
        ex_param_choice = pn.widgets.Select(name=message.get('from_repo_s3', 'param_ex_name'), options=ex_param_choices_dict[ex_pkg_choices[0]])
        button = pn.widgets.Button(name= message.get('from_repo_s3', 'end_choose'), button_type= "primary", width=300)
        button.on_click(choose_get_pkg_callback(ex_pkg_choice, ex_param_choice, button, from_repo_dict))
        ex_pkg_choice.param.watch(update_second_choices, 'value')
        display(ex_pkg_choice)
        display(ex_param_choice)
        display(button)

    else:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))


def choose_get_pkg_callback(ex_pkg_choice, ex_param_choice, button, from_repo_dict:dict):
    '''選択された実験パッケージ名、パラメータ実験名をファイルに記録する

    Args:
        ex_pkg_choice: 実験パッケージのpanel.widgets.Select
        ex_param_choice: パラメータ実験名のpanel.widgets.Select
        button: 入力完了ボタン
        from_repo_dict (dict): prepare_from_repositoryに記録する辞書
    '''

    def callback(event):
        '''選択された実験パッケージ名、パラメータ実験名をファイルに記録する
        '''

        from_repo_dict[EX_PKG_NAME] = ex_pkg_choice.value
        repo_name = from_repo_dict[REPO_NAME]
        ex_pkg_path = os.path.join(path.GET_REPO_PATH, repo_name, 'experiments', ex_pkg_choice.value)

        # 選択された実験パッケージ名、パラメータ実験名のフォルダが存在すること
        if not os.path.isdir(ex_pkg_path):
            button.button_type = 'danger'
            button.name = message.get('from_repo_s3', 'ex_pkg_not_selected')
            return

        if ex_param_choice is None:
            from_repo_dict[PARAM_EX_NAME] = ''
        else:
            from_repo_dict[PARAM_EX_NAME] = ex_param_choice.value
            ex_param_path = os.path.join(ex_pkg_path, ex_param_choice.value)

            if not os.path.isdir(ex_param_path):
                button.button_type = 'danger'
                button.name = message.get('from_repo_s3', 'ex_param_not_selected')
                return

        with open(path.FROM_REPO_JSON_PATH, 'w') as f:
            json.dump(from_repo_dict, f, indent=4)

        button.button_type = 'success'
        button.name = message.get('from_repo_s3', 'done_choose')
        return

    return callback


def choose_get_data():
    '''取得するデータを選択する
    '''


    def record_selected(event):
        '''選択されたデータをファイルに記録する
        '''

        # :リポジトリ名/ 以降の相対パスを格納する
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
            done_button.name = message.get('from_repo_s3', 'data_not_selected')
            return

        from_repo_dict[SELECTED_DATA] = selected_data_dict
        with open(path.FROM_REPO_JSON_PATH, 'w') as f:
            json.dump(from_repo_dict, f, indent=4)

        done_button.button_type = "success"
        done_button.name = message.get('from_repo_s3', 'done_choose')


    def get_files(target:str, parameter:str) -> list:
        '''input_data, source, output_data配下のファイルのパスを取得する

        Args:
            target (str): input_data, source, output_dataのいずれか
            parameter (str): パラメータ実験名

        Returns:
            list: input_data, source, output_data以降のファイルパスのリスト
        '''

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


    def generate_gui(files_dict:dict) -> list:
        '''MultiSelectに値を格納する

        Args:
            files_dict (dict): {input_data, source, output_dataのいずれか : ファイルパスのリスト}の辞書

        Returns:
            list: MultiSelectのリスト
        '''
        gui_list = []
        for key, value in files_dict.items():
            if key == 'input_data' or  key == 'source':
                gui_list.append(pn.widgets.MultiSelect(name=key, options=value, size=8, sizing_mode='stretch_width'))
            elif key == 'output_data':
                gui_list.append(pn.widgets.MultiSelect(name=os.path.join(parameter, key), options=value, size=8, sizing_mode='stretch_width'))
        return gui_list


    try:
        with open(path.FROM_REPO_JSON_PATH, 'r') as f:
            from_repo_dict:dict = json.load(f)
    except FileNotFoundError:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        return

    # 辞書のキーが存在すること
    if not {EX_PKG_NAME, PARAM_EX_NAME}.issubset(set(from_repo_dict.keys())):
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        return

    repo_name = from_repo_dict[REPO_NAME]
    package = from_repo_dict[EX_PKG_NAME]
    parameter = from_repo_dict[PARAM_EX_NAME]

    package_path = os.path.join(path.GET_REPO_PATH, repo_name, 'experiments', package)

    done_button = pn.widgets.Button(name= message.get('from_repo_s3', 'end_choose'), button_type= "primary")
    done_button.on_click(record_selected)

    # Generate a GUI that matches the configuration of the experimental package.
    input_data_files = get_files(target='input_data', parameter='')
    source_files = get_files(target='source', parameter='')
    output_data_files = get_files(target='output_data', parameter=parameter)
    files_dict = {"input_data":input_data_files, "source":source_files, "output_data":output_data_files}
    gui = generate_gui(files_dict)

    # Display GUI.
    pn.extension()
    columns = pn.Column()
    for column in gui:
        columns.append(column)
    columns.append(done_button)
    display(columns)


def input_path():
    '''データの格納先を入力するフォームを出力する
    '''


    def verify_input_text(event):
        '''入力された格納先を検証し、ファイルに記録する
        '''

        input_to_from_list = [(column.value_input, column.name) for column in columns if 'TextInput' in str(type(column))]
        experiment_title = ex_pkg_info.get_current_experiment_title()

        # 格納先パスの検証
        err_msg = validate.validate_input_path(input_to_from_list, experiment_title)
        if len(err_msg) > 0:
            done_button.button_type = "danger"
            done_button.name = err_msg
            return

        repository_path = os.path.join(path.GET_REPO_PATH, from_repo_dict[REPO_NAME])
        path_to_url_dict = dict()

        try:
            for input_to, input_from in input_to_from_list:

                # git annex whereisでURLを取得する
                result = git_module.git_annex_whereis('"{}"'.format(input_from), repository_path)
                input_url = ''
                if len(result) > 0:
                    data:dict = json.loads(result)
                    if KEY in data.keys() and 'URL' in data[KEY]:
                        input_url = data[WHEREIS][0][URLS][0].replace(' ', '%20')

                if len(input_url) == 0:
                    html_url = from_repo_dict[HTML_URL]
                    input_url = os.path.join(html_url, 'raw', 'master', input_from).replace(' ', '%20')

                input_to = os.path.join(path.HOME_PATH, 'experiments', experiment_title, input_to)
                path_to_url_dict[input_to] = input_url

        except Exception as e:
            error_message.value = str(e)
            return

        from_repo_dict[PATH_TO_URL] = path_to_url_dict
        with open(path.FROM_REPO_JSON_PATH, mode='w') as f:
            json.dump(from_repo_dict, f, indent=4)

        done_button.button_type = "success"
        done_button.name = message.get('from_repo_s3', 'done_input')


    try:
        with open(path.FROM_REPO_JSON_PATH, 'r') as f:
            from_repo_dict:dict = json.load(f)
    except FileNotFoundError:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        return

    if not SELECTED_DATA in from_repo_dict.keys():
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        return
    selected_data:dict = from_repo_dict[SELECTED_DATA]

    # 入力フォーム表示
    pn.extension()
    columns = pn.Column()
    for title, selected_paths in selected_data.items():
        if len(selected_paths) == 0:
            continue
        columns.append('### ' + title)
        for selected_path in selected_paths:
            columns.append(pn.widgets.TextInput(
                name = selected_path,
                placeholder = message.get('from_repo_s3', 'enter_a_file_path'),
                width = 700)
            )

    done_button = pn.widgets.Button(name= message.get('from_repo_s3', 'end_input'), button_type= "primary", width=300)
    columns.append(done_button)
    done_button.on_click(verify_input_text)
    error_message = pre.layout_error_text()
    columns.append(error_message)

    display(columns)


def prepare_addurls_data():
    """リポジトリへのリンク登録のためのcsvファイルを作成する

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合
        KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
    """
    try:
        with open(path.FROM_REPO_JSON_PATH, mode='r') as f:
            annex_util.create_csv(json.load(f)[PATH_TO_URL])
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        raise DidNotFinishError() from e
    except (KeyError, JSONDecodeError):
        display_util.display_err(message.get('from_repo_s3', 'unexpected'))
        raise


def add_url():
    """リポジトリに取得データのS3オブジェクトURLと格納先パスを登録する

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合
        IncompleteResultsError: addurlsに失敗した場合
    """
    try:
        annex_util.addurl(path.ADDURLS_CSV_PATH)
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        raise DidNotFinishError() from e
    except IncompleteResultsError:
        display_util.display_err(message.get('from_repo_s3', 'create_link_fail'))
        raise

    display_util.display_info(message.get('from_repo_s3', 'create_link_success'))


def save_annex():
    """データ取得履歴を記録する

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合
        KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
        UnexpectedError: 想定外のエラーが発生した場合
    """
    try:
        with open(path.FROM_REPO_JSON_PATH, mode='r') as f:
            from_repo_dict = json.load(f)
            path_to_url_dict:dict = from_repo_dict[PATH_TO_URL]
            repo_name = from_repo_dict[REPO_NAME]
            ex_pkg_name = from_repo_dict[EX_PKG_NAME]
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        raise DidNotFinishError() from e

    annex_file_paths = list(path_to_url_dict.keys())

    try:
        git_module.git_annex_lock(path.HOME_PATH)
        sync.save_annex_and_register_metadata(
            gitannex_path = annex_file_paths,
            gitannex_files = [],
            message = message.get('commit_message', 'from_repo').format(repo_name, ex_pkg_name))
    except Exception as e:
        display_util.display_err(message.get('from_repo_s3', 'process_fail'))
        raise UnexpectedError() from e
    else:
        clear_output()
        display_util.display_info(message.get('from_repo_s3', 'process_success'))


def get_data():
    """取得データの実データをダウンロードする

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合
        KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
        UnexpectedError: 想定外のエラーが発生した場合
    """

    try:
        with open(path.FROM_REPO_JSON_PATH, mode='r') as f:
            from_repo_dict = json.load(f)
        path_to_url_dict:dict = from_repo_dict[PATH_TO_URL]
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'not_finish_setup'))
        raise DidNotFinishError() from e
    except (KeyError, JSONDecodeError):
        display_util.display_err(message.get('from_repo_s3', 'unexpected'))
        raise

    annex_file_paths = list(path_to_url_dict.keys())

    try:
        experiment_title = ex_pkg_info.get_current_experiment_title()
        datalad_api.get(path=annex_file_paths)
        annex_util.annex_to_git(annex_file_paths, experiment_title)
    except Exception as e:
        display_util.display_err(message.get('from_repo_s3', 'process_fail'))
        raise UnexpectedError() from e
    else:
        clear_output()
        display_util.display_info(message.get('from_repo_s3', 'download_success'))


def remove_unused():
    '''クローンしてきたリポジトリが存在すれば削除する'''

    try:
        with open(path.FROM_REPO_JSON_PATH, 'r') as f:
            repo_name_path = os.path.join(path.GET_REPO_PATH, json.load(f)[REPO_NAME])
    except (FileNotFoundError, KeyError):
        return
    if os.path.isdir(repo_name_path):
        shutil.rmtree(repo_name_path)


def prepare_sync() -> dict:
    """同期の準備を行う

    Returns:
        dict: syncs_with_repoの引数が入った辞書
    Exception:
        DidNotFinishError: jsonファイルの形式が想定通りでない場合
        KeyError, JSONDecodeError: .tmp内のjsonファイルの形式が不正な場合
    """

    display(Javascript('IPython.notebook.save_checkpoint();'))
    experiment_title = experiment_title = ex_pkg_info.get_current_experiment_title()

    try:
        with open(path.FROM_REPO_JSON_PATH, mode='r') as f:
            from_repo_dict = json.load(f)
        path_to_url_dict:dict = from_repo_dict[PATH_TO_URL]
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'not_finish_setup'))
        raise DidNotFinishError() from e
    except (KeyError, JSONDecodeError):
        display_util.display_err(message.get('from_repo_s3', 'unexpected'))
        raise

    annex_file_paths = list(path_to_url_dict.keys())
    git_file_paths = []

    for annex_file_path in annex_file_paths:
        if annex_file_path.startswith(path.create_experiments_with_subpath(experiment_title, 'source/')):
            git_file_paths.append(annex_file_path)

    annex_file_paths = list(set(annex_file_paths) - set(git_file_paths))
    git_file_paths.append(path.EXP_DIR_PATH + path.PREPARE_FROM_REPOSITORY)

    sync_repo_args = dict()
    sync_repo_args['git_path'] = git_file_paths
    sync_repo_args['gitannex_path'] = annex_file_paths
    sync_repo_args['gitannex_files'] = annex_file_paths
    sync_repo_args['get_paths'] = [path.create_experiments_with_subpath(experiment_title)]
    sync_repo_args['message'] = message.get('commit_message', 'prepare_data').format(experiment_title)

    common.delete_file(path.FROM_REPO_JSON_PATH)
    common.delete_file(path.ADDURLS_CSV_PATH)

    return sync_repo_args
