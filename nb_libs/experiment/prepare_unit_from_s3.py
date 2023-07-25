import os, json, urllib, traceback
from ipywidgets import Text, Button, Layout
from IPython.display import display, clear_output, Javascript
from datalad import api
from nb_libs.utils.git import annex_util
from utils.path import path
from utils.message import message, display as display_util
from utils.gin import sync
from utils.common import common
from utils.git import git_module
from utils.aws import s3
from utils.except_class.addurls_err import DidNotFinishError

# 辞書のキー
S3_OBJECT_URL = 's3_object_url'
DEST_FILE_PATH = 'dest_file_path'
EX_PKG_NAME = 'ex_pkg_name'

def input_url_path():
    """S3オブジェクトURLと格納先パスをユーザから取得し、検証を行う

    """
    def on_click_callback(clicked_button: Button) -> None:

        common.delete_file(path.UNIT_S3_JSON_PATH)
        
        with open(path.PKG_INFO_PATH, mode='r') as f:
            experiment_title = json.load(f)[EX_PKG_NAME]

        input_url = text_url.value
        input_path = text_path.value

        err_msg = ""
        
        # URLの検証
        if len(input_url)<=0:
            err_msg = message.get('from_s3', 'empty_url')
        elif len(msg := (s3.access_s3_url(input_url))) > 0:
            err_msg = msg
        
        # 格納先パスの検証
        if len(err_msg) == 0:
            err_msg = s3.validate_input_path([(input_path, input_url)], experiment_title)

        if len(err_msg) > 0:
            button.layout=Layout(width='700px')
            button.button_style='danger'
            button.description = err_msg
            return

        data = dict()
        data[S3_OBJECT_URL] = urllib.parse.unquote(input_url)
        data[DEST_FILE_PATH] = path.create_experiments_sub_path(experiment_title, input_path)
        
        os.makedirs(path.RF_FORM_DATA_DIR, exist_ok=True)
        with open(path.UNIT_S3_JSON_PATH, mode='w') as f:
            json.dump(data, f, indent=4)

        button.description = message.get('from_s3', 'done_input')
        button.layout=Layout(width='250px')
        button.button_style='success'

    common.delete_file(path.UNIT_S3_JSON_PATH)
    style = {'description_width': 'initial'}
    text_path = Text(
        description = message.get('from_s3', 'file_path'),
        placeholder='Enter a file path here...',
        layout=Layout(width='700px'),
        style=style
    )
    text_url = Text(
        description=message.get('from_s3', 'object_url'),
        placeholder='Enter a object URL here...',
        layout=Layout(width='700px'),
        style=style
    )

    button = Button(description=message.get('from_s3', 'end_input'), layout=Layout(width='250px'))
    button.on_click(on_click_callback)
    display(text_url, text_path, button)

def prepare_addurls_data():
    """リポジトリへのリンク登録のためのcsvファイルを作成する

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合
        KeyError: .tmp内のjsonに指定したキーが存在しない場合

    """
    try:
        with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
            dic = json.load(f)
            input_url = dic[S3_OBJECT_URL]
            dest_path = dic[DEST_FILE_PATH]
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_s3', 'did_not_finish'))
        raise DidNotFinishError() from e
    except KeyError as e:
        display_util.display_err(message.get('from_s3', 'unexpected'))
        display_util.display_log(traceback.format_exc())
        raise KeyError() from e
    else:
        annex_util.create_csv({dest_path: input_url})

def add_url():
    """リポジトリに取得データのS3オブジェクトURLと格納先パスを登録する

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合
        AddurlsError: addurlsに失敗した場合
    """
    annex_util.addurl()
    display_util.display_info(message.get('from_s3', 'create_link_success'))

def save_annex():
    """データ取得履歴を記録する
    
    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合
        KeyError: .tmp内のjsonに指定したキーが存在しない場合
    """
    try:
        with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
            dest_path = json.load(f)[DEST_FILE_PATH]
        # The data stored in the source folder is managed by git, but once committed in git annex to preserve the history.
        # *No metadata is assigned to the annexed file because the actual data has not yet been acquired.
        annex_paths = [dest_path]
        git_module.git_annex_lock(path.HOME_PATH)
        sync.save_annex_and_register_metadata(gitannex_path=annex_paths, gitannex_files=[], message=message.get('from_s3', 'data_from_s3'))
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_s3', 'did_not_finish'))
        raise DidNotFinishError() from e
    except KeyError as e:
        display_util.display_err(message.get('from_s3', 'unexpected'))
        display_util.display_log(traceback.format_exc())
        raise KeyError() from e
    except Exception as e:
        display_util.display_err(message.get('from_s3', 'process_fail'))
        display_util.display_log(traceback.format_exc())
        raise Exception() from e
    else:
        clear_output()
        display_util.display_info(message.get('from_s3', 'process_success'))

def get_data():
    """取得データの実データをダウンロードする

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合
        KeyError: .tmp内のjsonに指定したキーが存在しない場合
    
    """
    try:
        # The data stored in the source folder is managed by git, but once committed in git annex to preserve the history.
        # *No metadata is assigned to the annexed file because the actual data has not yet been acquired.
        with open(path.PKG_INFO_PATH, mode='r') as f:
            experiment_title = json.load(f)[EX_PKG_NAME]
        with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
            dest_path = json.load(f)[DEST_FILE_PATH]

        annex_paths = [dest_path]
        # Obtain the actual data of the created link.
        api.get(path=annex_paths)
        annex_util.annex_to_git(annex_paths, experiment_title)
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_s3', 'did_not_finish'))
        raise DidNotFinishError() from e
    except KeyError as e:
        display_util.display_err(message.get('from_s3', 'unexpected'))
        display_util.display_log(traceback.format_exc())
        raise KeyError() from e
    except Exception as e:
        display_util.display_err(message.get('from_s3', 'process_fail'))
        display_util.display_log(traceback.format_exc())
        raise Exception() from e
    else:
        clear_output()
        display_util.display_info(message.get('from_s3', 'download_success'))

def prepare_sync() -> dict:
    """同期の準備を行う

    Returns:
        dict: syncs_with_repoの引数が入った辞書
    
    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合

    """

    display(Javascript('IPython.notebook.save_checkpoint();'))

    git_path = []
    try:
        with open(path.PKG_INFO_PATH, mode='r') as f:
            experiment_title = json.load(f)[EX_PKG_NAME]
        with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
            dest_path = json.load(f)[DEST_FILE_PATH]
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_s3', 'did_not_finish'))
        raise DidNotFinishError() from e
    except Exception as e:
        display_util.display_err(message.get('from_s3', 'unexpected'))
        display_util.display_log(traceback.format_exc())
        raise Exception() from e

    annex_paths = [dest_path]

    if dest_path.startswith(path.create_experiments_sub_path(experiment_title, 'source/')):
        git_path.append(dest_path)

    annex_paths = list(set(annex_paths) - set(git_path))
    git_path.append(path.EXP_DIR_PATH + path.PREPARE_UNIT_FROM_S3)

    sync_repo_args = dict()
    sync_repo_args['git_path'] = git_path
    sync_repo_args['gitannex_path'] = annex_paths
    sync_repo_args['gitannex_files'] = annex_paths
    sync_repo_args['get_paths'] = [path.create_experiments_sub_path(experiment_title)]
    sync_repo_args['message'] = message.get('from_s3', 'prepare_data').format(experiment_title)
    
    common.delete_file(path.UNIT_S3_JSON_PATH)
    common.delete_file(path.ADDURLS_CSV_PATH)
    
    return sync_repo_args