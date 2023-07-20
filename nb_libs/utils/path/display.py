from ..message import message, display
from . import path


def res_top_link():
    """研究フロートップページへのリンクを表示する"""
    display.desplay_link('./base_FLOW.ipynb', message.get("transition", "reserch_top"))


def res_top_link_from_maDMP():
    """研究フロートップページへのリンクを表示する"""
    top_path = os.path.join('./', path.FLOW_DIR, path.NOTEBOOK_DIR, path.RESEARCH_DIR, 'base_FLOW.ipynb')
    display.desplay_link(top_path, message.get("transition", "reserch_top"))


def exp_top_link():
    """実験フロートップページへのリンクを表示する"""
    display.desplay_link('./experimnet.ipynb', message.get("transition", "experiment_top"))