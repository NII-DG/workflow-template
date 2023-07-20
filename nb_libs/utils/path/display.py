import os
from ..message import message
from . import path


def move_button(url:str, msg:str):
    """同じページで画面遷移するボタンを表示する

    ARG
    ---------------
    url : str
        Description : リンク先のURL
    msg : str
        Description : 表示する説明
    """
    html_text = f'<button onclick="location.herf=\'{url}\'">{msg}</button>'
    return display(HTML(html_text))


def link_button(url:str, msg:str)
    """別タブでページを開くボタンを表示する

    ARG
    ---------------
    url : str
        Description : リンク先のURL
    msg : str
        Description : 表示する説明
    """
    html_text = f'<button onclick="window.open(\'{url}\')">{msg}</button>'
    return display(HTML(html_text))


def res_top_link():
    """研究フロートップページへのリンクを表示する"""
    move_button('./base_FLOW.ipynb', message.get("transition", "reserch_top"))


def res_top_link_from_maDMP():
    """研究フロートップページへのリンクを表示する"""
    top_path = os.path.join('./', path.FLOW_DIR, path.NOTEBOOK_DIR, path.RESEARCH_DIR, 'base_FLOW.ipynb')
    move_button(top_path, message.get("transition", "reserch_top"))


def exp_top_link():
    """実験フロートップページへのリンクを表示する"""
    move_button('./experimnet.ipynb', message.get("transition", "experiment_top"))