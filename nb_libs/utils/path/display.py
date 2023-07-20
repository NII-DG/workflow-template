import os
from IPython.display import display, HTML
from ..message import message
from . import path


def link_button(url:str, msg:str, target='_self'):
    """同じページで画面遷移するボタンを表示する

    Args:
        url (str): リンク先のURL
        msg (str): 表示する説明
        target (str): targetの属性(e.g. _blank)
    """
    html_text =  f'<a href="{url}" target="{target}" ><button>{msg}</button></a>'
    return display(HTML(html_text))


def res_top_link():
    """研究フロートップページへのリンクを表示する"""
    link_button('./base_FLOW.ipynb', message.get("transition", "reserch_top"))


def res_top_link_from_maDMP():
    """研究フロートップページへのリンクを表示する"""
    top_path = os.path.join('./', path.FLOW_DIR, path.NOTEBOOK_DIR, path.RESEARCH_DIR, 'base_FLOW.ipynb')
    link_button(top_path, message.get("transition", "reserch_top"))


def exp_top_link():
    """実験フロートップページへのリンクを表示する"""
    link_button('./experimnet.ipynb', message.get("transition", "experiment_top"))