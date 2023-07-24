import os
import json
import panel as pn
from IPython.display import display
from ..message import message
from ..message import display as show
from ..gin import sync
from ..git import git_module as git
from ..path import path
from ..path import display as link


def dg_menu(type='research'):
    """共通メニューを表示する"""
    pn.extension()

    menu_option = {}

    menu_option['--'] = 1

    if type == 'research':
        menu_option[message.get('menu', 'show_name_only_res')] = 2
        menu_option[message.get('menu', 'trans_reserch_top')] = 3

    elif type == 'experiment':
        menu_option[message.get('menu', 'show_name')] = 4
        menu_option[message.get('menu', 'trans_experiment_top')] = 5

    menu_option[message.get('menu', 'trans_gin')] = 6

    # プルダウン形式のセレクターを生成
    menu_selector = pn.widgets.Select(name=message.get('menu', 'select'), options=menu_option, value=1)

    html_output  = pn.pane.HTML()
    html_output.height = 50
    html_output.width = 400

    def update_selected_value(event):
        selected_value = event.new

        if selected_value == 1:
            html_output.object = ''
        elif selected_value == 2:
            html_output.object = html_res_name(color='green')
        elif selected_value == 3:
            html_output.object = link.res_top_html()
        elif selected_value == 4:
            html_text = html_res_name(color='blue') + html_exp_name(color='blue')
            html_output.object = html_text
        elif selected_value == 5:
            html_output.object = link.exp_top_html()
        elif selected_value == 6:
            html_output.object = gin_link_html()

    menu_selector.param.watch(update_selected_value,'value')
    html_output.height = 50
    html_output.width = 400
    display(menu_selector)
    display(html_output)


def html_res_name(color='black'):
    """研究名を表示する"""
    sync.update_repo_url()
    research_title = git.get_remote_url().split('/')[-1].replace('.git', '')
    msg = message.get('menu', 'research_title').format(research_title)
    return show.creat_html_msg(msg=msg, fore=color, tag='h1')


def html_exp_name(color='black'):
    """実験名を表示する"""
    try:
        file_path = os.path.join(path.SYS_PATH, 'ex_pkg_info.json')
        with open(file_path, mode='r') as f:
            info = json.load(f)
            experiment_title = info['ex_pkg_name']
    except Exception:
        experiment_title = '-'

    msg = message.get('menu', 'experiment_title').format(experiment_title)
    return show.creat_html_msg(msg=msg, fore=color, tag='h1')


def gin_link_html():
    """GIN-forkへの遷移のためのhtmlを生成する"""
    sync.update_repo_url()
    url = git.get_remote_url()
    return link.button_html(url=url, msg=message.get('menu', 'trans_gin'), target='_blank')