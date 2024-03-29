"""
リサーチフローで利用するパスを一括管理する
"""
import os


# directory
FLOW_DIR = "WORKFLOWS"
NOTEBOOK_DIR = "notebooks"
RESEARCH_DIR = "research"
EXPERIMENT_DIR = "experiment"
COMMON_DIR = 'common'
SNAKE_DOC_DIR = 'docs'

# notebook
RESEARCH_TOP = 'base_FLOW.ipynb'
BASE_VALIDATE_METADATA = 'base_validate_metadata.ipynb'
EXPERIMENT_TOP = 'experiment.ipynb'
PREPARE_FROM_REPOSITORY = 'prepare_from_repository.ipynb'
PREPARE_UNIT_FROM_S3 = 'prepare_unit_from_s3.ipynb'
PREPARE_MULTI_FROM_S3 = 'prepare_multi_from_s3.ipynb'
PREPARE_FROM_LOCAL = 'prepare_from_local.ipynb'
CONFLICT_HELPER = 'conflict_helper.ipynb'
SAVE = 'save.ipynb'

DESCRIBE_EXPERIMENT = 'describe_experiment.ipynb'
DESCRIBE_SNAKEFILE = 'describe_snakefile.ipynb'
HOW_TO_SNAKE_MAKE = 'HowToSnakemake.ipynb'

# other file
README_FILE = 'README.md'
SNAKE_FILE = 'Snakefile'

# path from inside container
## /home/jovyan
HOME_PATH = os.environ['HOME']
## Directory directly under /home/jovyan
SYS_PATH = os.path.join(HOME_PATH, '.dg-sys')
FROW_PATH = os.path.join(HOME_PATH, FLOW_DIR)
EXPERIMENTS_PATH = os.path.join(HOME_PATH, 'experiments')
VALIDATION_RESULTS_DIR_PATH = os.path.join(HOME_PATH, 'validation_results')

## Directory under /home/jovyan/WORKFLOWS
DATA_PATH = os.path.join(FROW_PATH, 'data')
RES_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, RESEARCH_DIR)
EXP_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, EXPERIMENT_DIR)
COMMON_DIR_PATH = os.path.join(FROW_PATH, NOTEBOOK_DIR, COMMON_DIR)

## File and Directory under /home/jovyan/.tmp/
TMP_DIR = os.path.join(HOME_PATH, '.tmp')
ADDURLS_CSV_PATH = os.path.join(TMP_DIR, 'datalad-addurls.csv')
RF_FORM_DATA_DIR = os.path.join(TMP_DIR, 'rf_form_data')
TMP_VALIDATION_DIR = os.path.join(TMP_DIR, 'validation')
GET_REPO_PATH = os.path.join(TMP_DIR, 'get_repo')
TMP_CONFLICT_DIR = os.path.join(TMP_DIR, 'conflict')

## File under /home/jovyan/.tmp/rf_form_data/
UNIT_S3_JSON_PATH = os.path.join(RF_FORM_DATA_DIR, 'prepare_unit_from_s3.json')
MULTI_S3_JSON_PATH = os.path.join(RF_FORM_DATA_DIR, 'prepare_multi_from_s3.json')
FROM_REPO_JSON_PATH = os.path.join(RF_FORM_DATA_DIR, 'prepare_from_repository.json')
FROM_LOCAL_JSON_PATH = os.path.join(RF_FORM_DATA_DIR, 'prepare_from_local.json')
SAVE_JSON_PATH = os.path.join(RF_FORM_DATA_DIR, 'save.json')

## File under /home/jovyan/.tmp/validation/
REQUEST_ID_FILE_PATH = os.path.join(TMP_VALIDATION_DIR, 'request_id.txt')



# path from outside container
URL_RES_PATH = os.path.join(FLOW_DIR, NOTEBOOK_DIR, RESEARCH_DIR, RESEARCH_TOP)
URL_EXP_PATH = os.path.join(FLOW_DIR, NOTEBOOK_DIR, EXPERIMENT_DIR, EXPERIMENT_TOP)


def create_experiments_with_subpath(experiment_title, sub_path=''):
    '''実験パッケージ配下の絶対パスを生成する

    Arg:
        experiment_title(str): 実験パッケージ名

        sub_path(str): 実験パッケージ配下のパス（オプション）
    Return:
        str: 実験パッケージ配下の絶対パス
    '''
    if len(sub_path) == 0:
        return os.path.join(EXPERIMENTS_PATH, experiment_title)
    else:
        return os.path.join(EXPERIMENTS_PATH, experiment_title, sub_path)
