import os, json, requests, urllib
from ipywidgets import Text, Button, Layout
from IPython.display import display

# メソッド名変える
def aaa():
    def on_click_callback(clicked_button: Button) -> None:
        os.chdir(os.environ['HOME'])
        with open('.dg-sys/ex_pkg_info.json', mode='r') as f:
            experiment_title = json.load(f)["ex_pkg_name"]

        input_path = text_path.value
        input_url = text_url.value

        # 全部returnにする
        if input_path.startswith('input_data/') or input_path.startswith('source/'):
            if os.path.isfile("experiments/" + experiment_title + "/" + input_path):
                button.description = f"`{input_path}` は既に存在するファイルです。修正後、再度クリックしてください。"
                button.layout=Layout(width='700px')
                button.button_style='danger'
            elif input_path == 'input_data/' or input_path == 'source/':
                button.description = f"`{input_path}` 以降が入力されていません。修正後、再度クリックしてください。"
                button.layout=Layout(width='700px')
                button.button_style='danger'
            elif len(input_url)<=0:
                button.description = "オブジェクトURLが空です。修正後、再度クリックしてください。"
                button.layout=Layout(width='700px')
                button.button_style='danger'
                return
            
            msg = access(input_url)
            if len(msg) > 0:
                button.description = msg
                button.layout=Layout(width='700px')
                button.button_style='danger'
            elif os.path.splitext(input_path)[1] != os.path.splitext(input_url)[1]:
                button.description = f"`{input_path}` の拡張子が元のファイルと一致しません。修正後、再度クリックしてください。"
                button.layout=Layout(width='700px')
                button.button_style='danger'
            else:
                button.description='入力を完了しました。'
                button.layout=Layout(width='250px')
                button.button_style='success'
        else:
            button.description='`input_data/`か`source/`で始まる必要があります。修正後、再度クリックしてください。'
            button.layout=Layout(width='700px')
            button.button_style='danger'

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

# 判定を直す
def access(url):
    
    response = requests.head(url)
    msg = ""
    if response.status_code == 200:
        pass
    elif response.status_code == 404 or response.status_code == 400:
        msg = 'URLが間違っています。'
    elif response.status_code == 403:
        msg = 'プライベートなオブジェクトです。'
    else:
        pass
    return msg