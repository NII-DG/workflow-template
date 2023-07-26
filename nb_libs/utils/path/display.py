"""メッセージを表示する必要のあるリンク"""
import os
from IPython.display import display, HTML
from ..message import message
from . import path


def button_html(url:str, msg:str, target='_self'):
    """画面遷移するボタンのhtmlを生成する

    Args:
        url (str): リンク先のURL
        msg (str): 表示する説明
        target (str): target属性の種類(e.g. _blank)
    """
    return f'<a class="selected-option" href="{url}" target="{target}" ><button>{msg}</button></a>'


def res_top_html():
    """研究フロートップページへのリンクのhtmlを生成する"""
    top_path = os.path.join('./', path.RESEARCH_TOP)
    return button_html(top_path, message.get("menu", "trans_reserch_top"))


def res_top_link():
    """研究フロートップページへのリンクを表示する"""
    html_text = res_top_html()
    display(HTML(html_text))


def res_top_link_from_maDMP():
    """研究フロートップページへのリンクを表示する"""
    top_path = os.path.join('./', path.FLOW_DIR, path.NOTEBOOK_DIR, path.RESEARCH_DIR, path.RESEARCH_TOP)
    html_text = button_html(top_path, message.get("menu", "trans_reserch_top"))
    display(HTML(html_text))


def exp_top_html():
    """実験フロートップページへのリンクのhtmlを生成する"""
    top_path = os.path.join('./', path.EXPERIMENT_TOP)
    return button_html(top_path, message.get("menu", "trans_experiment_top"))


def exp_top_link():
    """実験フロートップページへのリンクを表示する"""
    html_text = exp_top_html()
    display(HTML(html_text))