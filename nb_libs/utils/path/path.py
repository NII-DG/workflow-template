"""
リサーチフローで利用するパスを一括管理する
"""
import os


# directory
FLOW_DIR = "WORKFLOWS"
NOTEBOOK_DIR = "notebooks"
RESEARCH_DIR = "research"

# path
HOME_PATH = os.environ['HOME']
SYS_PATH = os.path.join(os.environ['HOME'], '.dg-sys')
FROW_PATH = os.path.join(os.environ['HOME'], FLOW_DIR)
EXPERIMENTS_PATH = os.path.join(os.environ['HOME'], 'experiments')

DATA_PATH = os.path.join(FROW_PATH, 'data')

RES_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, RESEARCH_DIR)
EXP_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, 'experiment')

def create_source_dir_path(experiment_title):
    '''sourceフォルダの絶対パスを生成する

    Arg:
        experiment_title 実験タイトル
    Return:
        sourceフォルダの絶対パス
    '''
    return os.path.join(os.environ['HOME'], 'experiments', experiment_title, 'source/')