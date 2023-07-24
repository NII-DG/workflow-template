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
HOME_PATH = os.environ['HOME']
SYS_PATH = os.path.join(os.environ['HOME'], '.dg-sys')
FROW_PATH = os.path.join(os.environ['HOME'], FLOW_DIR)
EXPERIMENTS_PATH = os.path.join(os.environ['HOME'], 'experiments')

DATA_PATH = os.path.join(FROW_PATH, 'data')
RES_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, RESEARCH_DIR)
EXP_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, EXPERIMENT_DIR)

# path from outside
URL_RES_PATH = os.path.join(FLOW_DIR, NOTEBOOK_DIR, RESEARCH_DIR, RESEARCH_TOP)
URL_EXP_PATH = os.path.join(FLOW_DIR, NOTEBOOK_DIR, EXPERIMENT_DIR, EXPERIMENT_TOP)


def create_source_dir_path(experiment_title):
    '''sourceフォルダの絶対パスを生成する

    Arg:
        experiment_title 実験タイトル
    Return:
        sourceフォルダの絶対パス
    '''
    return os.path.join(os.environ['HOME'], 'experiments', experiment_title, 'source/')
