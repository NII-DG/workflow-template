"""
リサーチフローで利用するパスを一括管理する
"""
import os
from ..message import message, display

# directory
FLOW_DIR = "WORKFLOWS"
NOTEBOOK_DIR = "notebooks"
RESEARCH_DIR = "research"

# path
SYS_PATH = os.path.join(os.environ['HOME'], '.dg-sys')
FROW_PATH = os.path.join(os.environ['HOME'], FLOW_DIR)

DATA_PATH = os.path.join(FROW_PATH, 'data')

RES_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, RESEARCH_DIR)
EXP_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, 'experiment')

def res_top_link():
    """研究フロートップページへのリンクを表示する"""
    display.desplay_link('./base_FLOW.ipynb', message.get("transition", "reserch_top"))


def res_top_link_from_maDMP():
    """研究フロートップページへのリンクを表示する"""
    path = os.path.join('./', FLOW_DIR, NOTEBOOK_DIR, RESEARCH_DIR, 'base_FLOW.ipynb')
    display.desplay_link(path, message.get("transition", "reserch_top"))


def exp_top_link():
    """実験フロートップページへのリンクを表示する"""
    display.desplay_link('experimnet.ipynb', message.get("transition", "experiment_top"))