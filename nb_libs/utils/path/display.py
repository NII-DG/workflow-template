"""メッセージを表示する必要のあるリンク"""
import os
from IPython.display import display, HTML
from ..message import message
from . import path


def button_html(
        url:str,
        msg:str,
        target='_self',
        a_character_color='#fff',
        a_font_size='15px',
        button_width='300px',
        button_height='30px',
        button_border_radius='5px',
        button_background_color='#2185d0',
        ):
    """画面遷移するボタンのhtmlを生成する

    Args:
        url (str): リンク先のURL
        msg (str): 表示する説明
        target (str): target属性の種類(e.g. _blank)
        a_character_color (str): (linkのスタイル) 文字カラー
        a_font_size (str): (リンクのスタイル) フォントサイズ
        button_width (str): (ボタンのスタイル) 幅
        button_height (str): (ボタンのスタイル) 高さ
        button_border_radius (str): (ボタンのスタイル) 角の丸み
        button_background_color (str): (ボタンのスタイル) 背景色
    """
    if target == '_blank':
        return f'<a style="color: {a_character_color}; font-size:{a_font_size};"href="{url}" target="{target}" rel="noopener"><button style="width: {button_width}; height: {button_height}; border-radius: {button_border_radius}; background-color: {button_background_color}; border: 0px none;">{msg}</button></a>'
    else:
        return f'<a style="color: {a_character_color}; font-size:{a_font_size};"href="{url}" target="{target}" ><button style="width: {button_width}; height: {button_height}; border-radius: {button_border_radius}; background-color: {button_background_color}; border: 0px none;">{msg}</button></a>'


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

def create_link(url, title, target='_blank'):
    return f'<a href="{url}" target="{target}">{title}</a>'
