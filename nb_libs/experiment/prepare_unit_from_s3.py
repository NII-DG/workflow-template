import os, json, urllib, csv, traceback
from ipywidgets import Text, Button, Layout
from IPython.display import display, clear_output, Javascript
from datalad import api
import nb_libs.utils.path.path as path
import nb_libs.utils.message.message as mess
import nb_libs.utils.message.display as display_util
import nb_libs.utils.gin.sync as sync
import nb_libs.utils.common.common as common
import nb_libs.utils.aws.s3 as s3
import nb_libs.utils.git.datalad_util as annex_util
import nb_libs.utils.git.git_module as git_module
from nb_libs.utils.except_class.addurls_err import AddurlsError

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
        
        if len(input_url)<=0:
            err_msg = mess.get('from_s3', 'empty_url')
        elif len(msg := (s3.access_s3_url(input_url))) > 0:
            err_msg = msg
        
        s3.validate_input_path()

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

        button.description = mess.get('from_s3', 'done_input')
        button.layout=Layout(width='250px')
        button.button_style='success'

    common.delete_file(path.UNIT_S3_JSON_PATH)
    style = {'description_width': 'initial'}
    text_path = Text(
        description = mess.get('from_s3', 'file_path'),
        placeholder='Enter a file path here...',
        layout=Layout(width='700px'),
        style=style
    )
    text_url = Text(
        description=mess.get('from_s3', 'object_url'),
        placeholder='Enter a object URL here...',
        layout=Layout(width='700px'),
        style=style
    )

    button = Button(description=mess.get('from_s3', 'end_input'), layout=Layout(width='250px'))
    button.on_click(on_click_callback)
    display(text_url, text_path, button)


def prepare_addurls_data():
    """リポジトリへのリンク登録のためのCSVファイルを作成する

    """
    try:
        with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
            dic = json.load(f)
            input_url = dic[S3_OBJECT_URL]
            dest_path = dic[DEST_FILE_PATH]
    except FileNotFoundError:
        display_util.display_err(mess.get('from_s3', 'did_not_finish'))
    except KeyError:
        display_util.display_err(mess.get('from_s3', 'unexpected'))
        display_util.display_log(traceback.format_exc())
    annex_util.create_csv({dest_path: input_url})

def add_url():
    """リポジトリに取得データのS3オブジェクトURLと格納先パスを登録する
    
    """
    try:
        result = ''
        result = api.addurls(save=False, fast=True, urlfile= path.ADDURLS_CSV_PATH, urlformat='{link}', filenameformat='{who}')

        for line in result:
            if 'addurls(error)' in line or 'addurls(impossible)' in line:
                raise AddurlsError
    except AddurlsError:
        display_util.display_err(mess.get('from_s3', 'create_link_fail'))
        display_util.display_log(traceback.format_exc())
    else:
        display_util.display_info(mess.get('from_s3', 'create_link_success'))

def save_annex():
    """データ取得履歴を記録する
    
    Exception:
    """
    try:
        with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
            dest_path = json.load(f)[DEST_FILE_PATH]

        # The data stored in the source folder is managed by git, but once committed in git annex to preserve the history.
        # *No metadata is assigned to the annexed file because the actual data has not yet been acquired.
        annex_paths = [dest_path]

        git_module.git_annex_lock()

        sync.save_annex_and_register_metadata(gitannex_path=annex_paths, gitannex_files=[], message=mess.get('from_s3', 'data_from_s3'))
    except Exception:
        display_util.display_err(mess.get('from_s3', 'process_fail'))
        display_util.display_log(traceback.format_exc())
    else:
        clear_output()
        display_util.display_info(mess.get('from_s3', 'process_success'))


def get_data():
    """取得データの実データをダウンロードする

    Exception:

    
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

        annex_util.annex_to_git(experiment_title)

        # if dest_path.startswith(path.create_experiments_sub_path(experiment_title, 'source/')):
        #     # Make the data stored in the source folder the target of git management.
        #     # Temporary lock on annex content
        #     common.exec_subprocess('git annex lock')
        #     # Unlock only the paths under the source folder.
        #     common.exec_subprocess(f'git annex unlock "{dest_path}"')
        #     common.exec_subprocess(f'git add "{dest_path}"')
        #     common.exec_subprocess('git commit -m "Change content type : git-annex to git"')
        #     common.exec_subprocess(f'git annex metadata --remove-all "{dest_path}"')
        #     common.exec_subprocess(f'git annex unannex "{dest_path}"')
        # else:
        #     # Attach sdDatePablished metadata to data stored in folders other than the source folder.
        #     sync.register_metadata_for_downloaded_annexdata(file_path=dest_path)

    except Exception:
        display_util.display_err(mess.get('from_s3', 'process_fail'))
        display_util.display_log(traceback.format_exc())
    else:
        clear_output()
        display_util.display_info(mess.get('from_s3', 'download_success'))

def prepare_sync() -> dict:
    """同期の準備を行う

    Return:
        dict: used in syncs_with_repo()

    """

    display(Javascript('IPython.notebook.save_checkpoint();'))

    git_path = []
    try:
        with open(path.PKG_INFO_PATH, mode='r') as f:
            experiment_title = json.load(f)[EX_PKG_NAME]
        with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
            dest_path = json.load(f)[DEST_FILE_PATH]
    except Exception:
        display_util.display_err(mess.get('from_s3', 'did_not_finish'))
        return

    annex_paths = [dest_path]

    if dest_path.startswith(path.create_experiments_sub_path(experiment_title, 'source/')):
        git_path.append(dest_path)

    annex_paths = list(set(annex_paths) - set(git_path))
    git_path.append(path.EXP_DIR_PATH + path.PREPARE_UNIT_FROM_S3)

    dic = dict()
    dic['git_path'] = git_path
    dic['gitannex_path'] = annex_paths
    dic['gitannex_files'] = annex_paths
    dic['get_paths'] = [path.create_experiments_sub_path(experiment_title)]
    dic['message'] = mess.get('from_s3', 'prepare_data').format(experiment_title)
    
    common.delete_file(path.UNIT_S3_JSON_PATH)
    common.delete_file(path.ADDURLS_CSV_PATH)
    
    return dic