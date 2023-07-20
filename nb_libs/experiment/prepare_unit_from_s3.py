import os, json, requests, urllib, csv, subprocess, traceback
from ipywidgets import Text, Button, Layout
from IPython.display import display, clear_output
import nb_libs.utils.path.path as path
import nb_libs.utils.message.message as mess
import nb_libs.utils.message.display as display_util
import nb_libs.utils.gin.sync as sync
import nb_libs.utils.gin.api as api

def input_url_path():
    """S3オブジェクトURLと格納先パスをユーザから取得し、検証を行う

    Exception:
        URLにアクセスして200,400,403,404以外のレスポンスが返ってきた場合
    """
    def on_click_callback(clicked_button: Button) -> None:
        
        os.chdir(os.environ['HOME'])
        with open(os.path.join(path.SYS_PATH, 'ex_pkg_info.json'), mode='r') as f:
            experiment_title = json.load(f)["ex_pkg_name"]

        input_url = text_url.value
        input_path = text_path.value

        err_msg = ""
        
        if len(input_url)<=0:
            err_msg = mess.get('from_s3', 'empty_url')
        elif len(msg := (validate_url(input_url))) > 0:
            err_msg = msg

        elif not input_path.startswith('input_data/') and not input_path.startswith('source/'):
            err_msg = mess.get('from_s3', 'start_with')
        elif input_path == 'input_data/' or input_path == 'source/':
            err_msg = input_path + mess.get('from_s3', 'after_dir')
        elif os.path.isfile(os.path.join("experiments", experiment_title, input_path)):
            err_msg = input_path + mess.get('from_s3', 'already_exist')

        elif os.path.splitext(input_path)[1] != os.path.splitext(input_url)[1]:
            err_msg = input_path + mess.get('from_s3', 'different_url')

        if len(err_msg) > 0:
            button.layout=Layout(width='700px')
            button.button_style='danger'
            button.description = err_msg
            return

        data = dict()
        data['s3_object_url'] = urllib.parse.quote(input_url)
        data['dest_file_path'] = input_path
        
        os.makedirs('.tmp/rf_form_data', exist_ok=True)
        with open(os.path.join(os.environ['HOME'], '.tmp/rf_form_data/prepare_unit_from_s3.json'), mode='w') as f:
            json.dump(data, f, indent=4)

        button.description = mess.get('from_s3', 'end_input')
        button.layout=Layout(width='250px')
        button.button_style='success'

    button = Button(description=mess.get('from_s3', 'end_input'), layout=Layout(width='250px'))
    button.on_click(on_click_callback)
    text_url.on_submit(on_click_callback)
    display(text_url, text_path, button)

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

def validate_url(url):
    msg = ""
    try:
        response = requests.head(url)
        if response.status_code == 200:
            pass
        elif response.status_code == 404 or response.status_code == 400:
            msg = mess.get('from_s3', 'wrong_url')
        elif response.status_code == 403:
            msg = mess.get('from_s3', 'private_url')
        else:
            raise Exception("想定外のエラーが発生しました。担当者に問い合わせください。")
    except requests.exceptions.RequestException:
        msg = mess.get('from_s3', 'wrong_url')
    return msg

def create_csv():
    """リポジトリへのリンク登録のためのCSVファイルを作成する
    
    Exception:
        jsonファイルから情報を取得できなかった場合
    """
    with open(os.path.join(os.environ['HOME'], '.tmp/rf_form_data/prepare_unit_from_s3.json'), mode='r') as f:
        dic = json.load(f)
        input_url = dic['s3_object_url']
        dest_path = dic['dest_file_path']

        with open(os.path.join(os.environ['HOME'], '.tmp/datalad-addurls.csv'), mode='w') as f:
            writer = csv.writer(f)
            writer.writerow(['who','link'])
            writer.writerow([dest_path, input_url])

def add_url():
    """リポジトリに取得データのS3オブジェクトURLと格納先パスを登録する
    
    Exception:
    """
    try:
        result = ''
        result = subprocess.getoutput("datalad addurls --nosave --fast .tmp/datalad-addurls.csv '{link}' '{who}'")

        for line in result:
            if 'addurls(error)' in line or 'addurls(impossible)' in line:
                raise Exception
    except Exception:
        display_util.display_err("リンクの作成に失敗しました。用意したいデータにアクセス可能か確認してください。")
        display_util.display_log(traceback.format_exc())
    else:
        display_util.display_info("リンクの作成に成功しました。次の処理にお進みください。")

def save_annex():
    """データ取得履歴を記録する
    
    Exception:
    """
    try:
        with open(os.path.join(path.SYS_PATH, 'ex_pkg_info.json'), mode='r') as f:
            experiment_title = json.load(f)["ex_pkg_name"]
        with open(os.path.join(os.environ['HOME'], '.tmp/rf_form_data/prepare_unit_from_s3.json'), mode='r') as f:
            input_path = json.load(f)['dest_file_path']
        dest_path = os.path.join(path.EXP_DIR_PATH, experiment_title, input_path)
        # The data stored in the source folder is managed by git, but once committed in git annex to preserve the history.
        os.chdir(os.environ['HOME'])
        # *No metadata is assigned to the annexed file because the actual data has not yet been acquired.
        annex_pahts = [dest_path]
        os.system('git annex lock')
        sync.save_annex_and_register_metadata(gitannex_path=annex_pahts, gitannex_files=[], message='S3ストレージから実験のデータを用意')
    except Exception:
        display_util.display_err("処理に失敗しました。用意したいデータにアクセス可能か確認してください。")
        display_util.display_log(traceback.format_exc())
    else:
        clear_output()
        display_util.display_info("来歴の記録とデータのダウンロードに成功しました。次の処理にお進みください。")


def get_data():
    """取得データの実データをダウンロードする

    Exception:
    """
    git_path = []
    try:
        # The data stored in the source folder is managed by git, but once committed in git annex to preserve the history.
        os.chdir(os.environ['HOME'])
        # *No metadata is assigned to the annexed file because the actual data has not yet been acquired.
        with open(os.path.join(path.SYS_PATH, 'ex_pkg_info.json'), mode='r') as f:
            experiment_title = json.load(f)["ex_pkg_name"]
        with open(os.path.join(os.environ['HOME'], '.tmp/rf_form_data/prepare_unit_from_s3.json'), mode='r') as f:
            input_path = json.load(f)['dest_file_path']
        dest_path = '/home/jovyan/experiments/' + experiment_title + '/' + input_path

        annex_pahts = [dest_path]
        # Obtain the actual data of the created link.
        api.get(path=annex_pahts)

        if input_path.startswith('source/'):
            # Make the data stored in the source folder the target of git management.
            # Temporary lock on annex content
            subprocess.getoutput('git annex lock')
            # Unlock only the paths under the source folder.
            subprocess.getoutput(f'git annex unlock "{dest_path}"')
            subprocess.getoutput(f'git add "{dest_path}"')
            subprocess.getoutput('git commit -m "Change content type : git-annex to git"')
            subprocess.getoutput(f'git annex metadata --remove-all "{dest_path}"')
            subprocess.getoutput(f'git annex unannex "{dest_path}"')
            git_path.append(dest_path)
        else:
            # Attach sdDatePablished metadata to data stored in folders other than the source folder.
            sync.register_metadata_for_downloaded_annexdata(file_path=dest_path)

        annex_paths = list(set(annex_pahts) - set(git_path))

    except Exception:
        display_util.display_err("処理に失敗しました。用意したいデータにアクセス可能か確認してください。")
        display_util.display_log(traceback.format_exc())
    else:
        clear_output()
        display_util.display_info("来歴の記録とデータのダウンロードに成功しました。次の処理にお進みください。")