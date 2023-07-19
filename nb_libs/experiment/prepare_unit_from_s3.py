import os, json, requests, urllib, csv
from ipywidgets import Text, Button, Layout
from IPython.display import display
import nb_libs.utils.path.path

# メソッド名変える
def aaa():
    def on_click_callback(clicked_button: Button) -> None:
        
        os.chdir(os.environ['HOME'])
        with open(os.path.join(nb_libs.utils.path.path.SYS_PATH, 'ex_pkg_info.json'), mode='r') as f:
            experiment_title = json.load(f)["ex_pkg_name"]

        input_url = text_url.value
        input_path = text_path.value

        err_msg = ""
        
        if len(input_url)<=0:
            err_msg = "オブジェクトURLが空です。修正後、再度クリックしてください。"
        elif len(msg := (access(input_url))) > 0:
            err_msg = msg

        elif not input_path.startswith('input_data/') and not input_path.startswith('source/'):
            err_msg='`input_data/`か`source/`で始まる必要があります。修正後、再度クリックしてください。'
        elif input_path == 'input_data/' or input_path == 'source/':
            err_msg = f"`{input_path}` 以降が入力されていません。修正後、再度クリックしてください。"
        elif os.path.isfile("experiments/" + experiment_title + "/" + input_path):
            err_msg = f"`{input_path}` は既に存在するファイルです。修正後、再度クリックしてください。"

        elif os.path.splitext(input_path)[1] != os.path.splitext(input_url)[1]:
            err_msg = f"`{input_path}` の拡張子が元のファイルと一致しません。修正後、再度クリックしてください。"

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

        button.description='入力を完了しました。'
        button.layout=Layout(width='250px')
        button.button_style='success'

    button = Button(description='入力を完了する',layout=Layout(width='250px'))
    button.on_click(on_click_callback)
    text_url.on_submit(on_click_callback)
    display(text_url, text_path, button)

style = {'description_width': 'initial'}
text_path = Text(
    description='*格納先のファイルパス：',
    placeholder='Enter a file path here...',
    layout=Layout(width='700px'),
    style=style
)
text_url = Text(
    description='*S3にあるデータのオブジェクトURL：',
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
            msg = 'URLが間違っています。'
        elif response.status_code == 403:
            msg = 'プライベートなオブジェクトです。'

    except requests.exceptions.RequestException:
        msg = 'URLが間違っています。'
    return msg

def bbb():
    with open(os.path.join(os.environ['HOME'], '.tmp/rf_form_data/prepare_unit_from_s3.json'), mode='r') as f:
        input_url = json.load(f)['s3_object_url']
        dest_path = json.load(f)['dest_file_path']

        with open(os.path.join(os.environ['HOME'], '.tmp/datalad-addurls.csv'), mode='w') as f:
            writer = csv.writer(f)
            writer.writerow(['who','link'])
            writer.writerow([dest_path, input_url])