"""
リサーチフローで利用するパスを一括管理する
"""
import os


# directory
FLOW_DIR = "WORKFLOWS"
NOTEBOOK_DIR = "notebooks"
RESEARCH_DIR = "research"
EXPERIMENT_DIR = "experiment"

# notebook
RESEARCH_TOP = 'base_FLOW.ipynb'
EXPERIMENT_TOP = 'experiment.ipynb'

# path from inside
SYS_PATH = os.path.join(os.environ['HOME'], '.dg-sys')
FROW_PATH = os.path.join(os.environ['HOME'], FLOW_DIR)
EXPERIMENTS_PATH = os.path.join(os.environ['HOME'], 'experiments')

DATA_PATH = os.path.join(FROW_PATH, 'data')
RES_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, RESEARCH_DIR)
EXP_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, EXPERIMENT_DIR)

# path from outside
URL_RES_PATH = os.path.join(FLOW_DIR, NOTEBOOK_DIR, RESEARCH_DIR, RESEARCH_TOP)
URL_EXP_PATH = os.path.join(FLOW_DIR, NOTEBOOK_DIR, EXPERIMENT_DIR, EXPERIMENT_TOP)