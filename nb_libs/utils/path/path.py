"""
リサーチフローで利用するパスを一括管理する
"""
import json
import os


# directory
FLOW_DIR = "WORKFLOWS"
NOTEBOOK_DIR = "notebooks"
RESEARCH_DIR = "research"
EXPERIMENT_DIR = "experiment"

# notebook
RESEARCH_TOP = 'base_FLOW.ipynb'
EXPERIMENT_TOP = 'experiment.ipynb'
PREPARE_FROM_REPOSITORY = 'prepare_from_repository.ipynb'
PREPARE_UNIT_FROM_S3 = 'prepare_unit_from_s3.ipynb'
PREPARE_MULTI_FROM_S3 = 'prepare_multi_from_s3.ipynb'
PREPARE_FROM_LOCAL = 'prepare_from_local.ipynb'

DESCRIBE_EXPERIMENT = 'describe_experiment.ipynb'
DESCRIBE_SNAKEFILE = 'describe_snakefile.ipynb'
HOW_TO_SNAKE_MAKE = 'HowToSnakemake.ipynb'

# other file
README_FILE = 'README.md'
SNAKE_FILE = 'Snakefile'

# path from inside
HOME_PATH = os.environ['HOME']
SYS_PATH = os.path.join(os.environ['HOME'], '.dg-sys')
FROW_PATH = os.path.join(os.environ['HOME'], FLOW_DIR)

DATA_PATH = os.path.join(FROW_PATH, 'data')
RES_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, RESEARCH_DIR)
EXP_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, EXPERIMENT_DIR)

PKG_INFO_PATH = os.path.join(SYS_PATH, 'ex_pkg_info.json')
ADDURLS_CSV_PATH = os.path.join(os.environ['HOME'], '.tmp/datalad-addurls.csv')
RF_FORM_DATA_DIR = os.path.join(os.environ['HOME'], '.tmp/rf_form_data')
UNIT_S3_JSON_PATH = os.path.join(RF_FORM_DATA_DIR, 'prepare_unit_from_s3.json')
SNAKE_DOC_PATH = os.path.join(EXP_DIR_PATH, 'docs')

# path from outside
URL_RES_PATH = os.path.join(FLOW_DIR, NOTEBOOK_DIR, RESEARCH_DIR, RESEARCH_TOP)
URL_EXP_PATH = os.path.join(FLOW_DIR, NOTEBOOK_DIR, EXPERIMENT_DIR, EXPERIMENT_TOP)


def create_experiments_sub_path(experiment_title, sub_path=''):
    '''実験パッケージ配下の絶対パスを生成する

    Arg:
        experiment_title 実験パッケージ名
        sub_path 実験パッケージ配下のパス
    Return:
        experimentsフォルダ配下の絶対パス
    '''
    if len(sub_path) == 0:
        return os.path.join(os.environ['HOME'], 'experiments', experiment_title)
    else:
        return os.path.join(os.environ['HOME'], 'experiments', experiment_title, sub_path)


def get_current_experiment_title():
    '''現在実験中の実験パッケージ名を取得する

    Arg:
        なし
    Return:
        現在実験中の実験パッケージ名 (初期設定が未完了の場合はNone)
    '''
    try:
        with open(PKG_INFO_PATH, mode='r') as f:
            return json.load(f)['ex_pkg_name']
    except Exception:
        return None
