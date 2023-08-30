import os
import json
import panel as pn
from IPython.display import display, clear_output, Javascript
from ..message import message as msg_mod, display as msg_display
from ..path import path, display as path_display
from ..common import common
from ..gin import sync
from ..git import git_module as git
from . import prepare as pre
# To remove the git config warning message on module import with execution result
clear_output()


def dg_menu(type='research'):
    """共通メニューを表示する"""
    pn.extension()

    menu_option = {}

    menu_option[pre.SELECT_DEFAULT_VALUE] = 1

    if type == 'research':
        menu_option[msg_mod.get('menu', 'show_name_only_res')] = 2
        menu_option[msg_mod.get('menu', 'trans_reserch_top')] = 3

    elif type == 'experiment':
        menu_option[msg_mod.get('menu', 'show_name')] = 4
        menu_option[msg_mod.get('menu', 'trans_experiment_top')] = 5
    elif type == 'conflict':
        menu_option[msg_mod.get('menu', 'show_name')] = 4
    elif type == 'research_top':
        menu_option[msg_mod.get('menu', 'show_name_only_res')] = 2
    elif type == 'experiment_top':
        menu_option[msg_mod.get('menu', 'show_name')] = 4

    menu_option[msg_mod.get('menu', 'trans_gin')] = 6

    # プルダウン形式のセレクターを生成
    menu_selector = pn.widgets.Select(name=msg_mod.get('menu', 'select'), options=menu_option, value=1, width=350)

    html_output  = pn.pane.HTML()

    def update_selected_value(event):
        selected_value = event.new

        if selected_value == 1:
            html_output.object = ''
            html_output.height = 10
            html_output.width = 900
        elif selected_value == 2:
            html_output.object = html_res_name(color='green')
            html_output.height = 60
            html_output.width = 900
        elif selected_value == 3:
            html_output.object = path_display.res_top_html()
            html_output.height = 30
            html_output.width = 900
        elif selected_value == 4:
            html_text = html_res_name(color='blue') + html_exp_name(color='blue')
            html_output.object = html_text
            html_output.height = 110
            html_output.width = 900
        elif selected_value == 5:
            html_output.object = path_display.exp_top_html()
            html_output.height = 30
            html_output.width = 900
        elif selected_value == 6:
            html_output.object = gin_link_html()
            html_output.height = 30
            html_output.width = 900

    menu_selector.param.watch(update_selected_value,'value')

    display(pn.Column(menu_selector, html_output))
    display(Javascript('IPython.notebook.save_checkpoint();'))


def html_res_name(color='black'):
    """研究名を表示する"""
    try:
        sync.update_repo_url()
    except Exception:
        pass

    research_title = git.get_remote_url().split('/')[-1].replace('.git', '')
    msg = msg_mod.get('menu', 'research_title').format(research_title)
    return msg_display.creat_html_msg(msg=msg, fore=color, tag='h1')


def html_exp_name(color='black'):
    """実験名を表示する"""
    try:
        file_path = os.path.join(path.SYS_PATH, 'ex_pkg_info.json')
        with open(file_path, mode='r') as f:
            info = json.load(f)
            experiment_title = info['ex_pkg_name']
    except Exception:
        experiment_title = '-'

    msg = msg_mod.get('menu', 'experiment_title').format(experiment_title)
    return msg_display.creat_html_msg(msg=msg, fore=color, tag='h1')


def gin_link_html():
    """GIN-forkへの遷移のためのhtmlを生成する"""
    try:
        sync.update_repo_url()
    except Exception:
        pass

    url , _ = common.convert_url_remove_user_token(git.get_remote_url())
    return path_display.button_html(url=url, msg=msg_mod.get('menu', 'trans_gin'), target='_blank')
