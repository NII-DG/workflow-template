import os, json, requests, urllib, csv
from ipywidgets import Text, Button, Layout
from IPython.display import display
import nb_libs.utils.path.path
import nb_libs.utils.message as mess

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
            msg = mess.get('from_s3', 'wrong_url'),
        elif response.status_code == 403:
            msg = mess.get('from_s3', 'private_url'),
    except requests.exceptions.RequestException:
        msg = mess.get('from_s3', 'wrong_url'),
    return msg

def bbb():
    with open(os.path.join(os.environ['HOME'], '.tmp/rf_form_data/prepare_unit_from_s3.json'), mode='r') as f:
        input_url = json.load(f)['s3_object_url']
        dest_path = json.load(f)['dest_file_path']

        with open(os.path.join(os.environ['HOME'], '.tmp/datalad-addurls.csv'), mode='w') as f:
            writer = csv.writer(f)
            writer.writerow(['who','link'])
            writer.writerow([dest_path, input_url])