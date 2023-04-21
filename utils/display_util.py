"""
HTMMを生成して任意のメッセージを表示されるモジュール
jupyterNotebookのセルの実行結果に表示させることを前提としている。
"""
from IPython.display import display, HTML


def creat_html_msg(msg='', fore=None, back=None, tag='h1'):
    """HTMLを生成して表示するメソッド
    ARG
    ---------------
    msg : str
        Description : メッセージ文字列
        Default : ''
    fore : str
        Description : 文字色
        Default : None
    back : str
        Description : 背景色
        Default : None
    tag : str
        Description : HTMLタグ
        Default : 'h1'
    """
    if fore is not None and back is not None:
        style: str = 'color:' + fore + ';' + 'background-color:' + back + ";"
    elif fore is not None and back is None:
        style = 'color:' + fore
    elif fore is None and back is not None:
        style = 'background-color:' + back
    else:
        style = ""

    if style != "":
        return "<" + tag + " style='" + style + "'>" + msg + "</" + tag + ">"
    else:
        return "<" + tag + " style='" + style + "'>" + msg + "</" + tag + ">"

def display_msg(msg='', fore=None, back=None, tag='h1'):
    """HTMLを生成して表示するメソッド
    ARG
    ---------------
    msg : str
        Description : メッセージ文字列
        Default : ''
    fore : str
        Description : 文字色
        Default : None
    back : str
        Description : 背景色
        Default : None
    tag : str
        Description : HTMLタグ
        Default : 'h1'
    """
    html_text = creat_html_msg(msg, None, back, default_tag)
    display(HTML(html_text))


default_tag = "p"
"""メソッド : display_info()、display_err()、display_warm()のデフォルトのHTMLタグ種
"""


def display_info(msg=''):
    """正常メッセージ出力メソッド(h2タグの背景色(#9eff9e))
    ARG
    ---------------
    msg : str
        Description : メッセージ文字列
        Default : ''
    """
    back = "#9eff9e"
    html_text = creat_html_msg(msg, None, back, default_tag)
    display(HTML(html_text))


def display_err(msg=''):
    """異常メッセージ出力メソッド(h2タグの背景色(#ffa8a8))
    ARG
    ---------------
    msg : str
        Description : メッセージ文字列
        Default : ''
    """
    back = "#ffa8a8"
    html_text = creat_html_msg(msg, None, back, default_tag)
    display(HTML(html_text))


def display_warm(msg=''):
    """警告メッセージ出力メソッド(h2タグの背景色(#ffff93))
    ARG
    ---------------
    msg : str
        Description : メッセージ文字列
        Default : ''
    """
    back = "#ffff93"
    html_text = creat_html_msg(msg, None, back, default_tag)
    display(HTML(html_text))
