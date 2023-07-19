"""
リサーチフローで利用するパスを一括管理する
"""
import os
import sys
sys.path.append('..')
from message import message, display

# directory
NOTEBOOK_DIR = "notebooks"

# path
SYS_PATH = os.path.join(os.environ['HOME'], '.dg-sys')
FROW_PATH = os.path.join(os.environ['HOME'], "WORKFLOWS")
DATA_PATH = os.path.join(FROW_PATH, "data")

RES_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, "research")
EXP_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, "experiment")

RES_TOP_PATH = os.path.join(RES_DIR_PATH, "base_FLOW.ipynb")
EXP_TOP_PATH = os.path.join(EXP_DIR_PATH, "experiment.ipynb")


def res_top_link():
    """研究フロートップページへのリンクを表示する"""
    return display.desplay_link(RES_TOP_PATH, message.get("transition", "reserch_top"))


def exp_top_link():
    """実験フロートップページへのリンクを表示する"""
    return display.desplay_link(EXP_TOP_PATH, message.get("transition", "experiment_top"))