"""
リサーチフローで利用するパスを一括管理する
"""
import os


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