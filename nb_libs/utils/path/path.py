"""
リサーチフローで利用するパスを一括管理する
"""
import os
import sys
sys.path.append('..')
from message import message, display

# directory
FROW_DIR = "WORKFLOWS"
NOTEBOOK_DIR = "notebooks"
RES_DIR = "research"
EXP_DIR = "experiment"

# notebook
RES_TOP_NB = "base_FLOW.ipynb"
EXP_TOP_NB = "experiment.ipynb"

# path
SYS_PATH = os.path.join(os.environ['HOME'], '.dg-sys')
FROW_PATH = os.path.join(os.environ['HOME'], FROW_DIR)

RES_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, RES_DIR)
EXP_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, EXP_DIR)

RES_TOP_PATH = os.path.join(RES_DIR_PATH, RES_TOP_NB)
EXP_TOP_PATH = os.path.join(EXP_DIR_PATH, EXP_TOP_NB)


def res_top_link():
    """研究フロートップページへのリンクを表示する"""
    return display.desplay_link(RES_TOP_PATH, message.get("transition", "reserch_top"))


def exp_top_link():
    """実験フロートップページへのリンクを表示する"""
    return display.desplay_link(EXP_TOP_PATH, message.get("transition", "experiment_top"))