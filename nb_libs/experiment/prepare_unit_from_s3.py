import os, json, requests, urllib, csv, subprocess, traceback
from ipywidgets import Text, Button, Layout
from IPython.display import display
import nb_libs.utils.path.path
import nb_libs.utils.message.message as mess
import nb_libs.utils.message.display as display_util

# メソッド名変える
def aaa():
    """S3オブジェクトURLと格納先パスをユーザから取得し、検証を行う

    Exception:
        URLにアクセスして200,400,403,404以外のレスポンスが返ってきた場合
    """
    def on_click_callback(clicked_button: Button) -> None:
        
        os.chdir(os.environ['HOME'])
        with open(os.path.join(nb_libs.utils.path.path.SYS_PATH, 'ex_pkg_info.json'), mode='r') as f:
            experiment_title = json.load(f)["ex_pkg_name"]

        input_url = text_url.value
        input_path = text_path.value

        err_msg = ""
        
        if len(input_url)<=0:
            err_msg = mess.get('from_s3', 'empty_url')
        elif len(msg := (access(input_url))) > 0:
            err_msg = msg

        elif not input_path.startswith('input_data/') and not input_path.startswith('source/'):
            err_msg = mess.get('from_s3', 'start_with')
        elif input_path == 'input_data/' or input_path == 'source/':
            err_msg = input_path + mess.get('from_s3', 'after_dir')
        elif os.path.isfile("experiments/" + experiment_title + "/" + input_path):
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

def access(url):
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

def bbb():
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

def ccc():
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

# def ddd():
    