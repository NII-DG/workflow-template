import os
from ..utils.params import ex_pkg_info as epi
from ..utils.path import path, display as pd
from ..utils.message import message, display as md
from ..utils.git import git_module as git
from ..utils.common import common, file_operation as fo
from ..utils.except_class import DGTaskError
from IPython.display import HTML, display



def analyze_conflict_status():
    """1. 競合状態の解析
    """
    # check exist conflict_helper.json
    if exist_rf_form_file():
        ## No processing is performed because this task is running
        ## Display error message to user and terminate the process
        err_msg = message.get('task', 'in_progress')
        md.display_err(err_msg)
        return

    try:
        # Start analyzing the state of contention
        ## Disable git output encoding
        git.disable_encoding_git()
        ## Obtain a list of file paths that have conflicts (conflict file path list).
        conflict_file_path_list = git.get_conflict_filepaths()
        ## If the length of the conflict file path list is 0, no conflict has occurred.
        if len(conflict_file_path_list) < 1:
            # Display to the user that the task does not need to be executed, and terminate the process.
            err_msg = message.get('conflict_helper', 'no_need_exec_task')
            md.display_warm(err_msg)
            git.enable_encoding_git()
            return

        ## Obtain a list of Annex content paths in the repository (Annex file path list)
        annex_file_path_list = git.get_annex_content_file_paht_list()
        ## Get the list of Annex file paths where conflicts are occurring.
        annex_conflict_file_path_list = common.get_AND_elements(conflict_file_path_list, annex_file_path_list)
        ## Get the list of Git file paths where conflicts are occurring.
        git_conflict_file_path_list = list(set(conflict_file_path_list) - set(annex_conflict_file_path_list))
        # Separate Task Notebook files from other files
        git_auto_conflict_filepaths, git_custom_conflict_filepaths = divide_rf_notebook_or_non_file(git_conflict_file_path_list)

        # Save the data of the task Notebook in which the conflict occurred to a temporary file.
        save_task_notebooks_to_tmp(git_auto_conflict_filepaths)

        # Save git_conflict_file_path_list, git_auto_conflict_filepaths,
        # git_custom_conflict_filepaths, annex_conflict_file_path_list to .tmp/rf_form_data/conflict_helper.json
        record_rf_data_conflict_info(
            git_conflict_file_path_list,
            git_auto_conflict_filepaths,
            git_custom_conflict_filepaths,
            annex_conflict_file_path_list
            )
    except Exception as e:
        err_msg = message.get('DEFAULT', 'unexpected')
        md.display_err(err_msg)
        git.enable_encoding_git()
        raise e
    else:
        ## Prompts operation of the next section
        msg = message.get('conflict_helper', 'finish_analyze_conflict')
        md.display_info(msg)




def get_annex_variatns():
    """2-1. annex競合バリアントファイルの入手
    """
    pass

def record_preparing_event_for_resolving_conflict():
    """2-2. 競合解消準備をリポジトリ履歴に記録
    """
    pass

def resolving_git_content():
    """3-1. gitコンテンツの競合解消
    """
    pass

def select_action_for_resolving_annex():
    """3-2. Annexコンテンツの競合解消アクションを選択
    """
    pass

def rename_variants():
    """3-3. ≪両方を残す≫を選択したファイル名の入力
    """
    pass

def auto_resolve_task_notebooks():
    """4-1. データの調整 - タスクNotebookの自動解消
    """
    pass

def adjust_annex_data():
    """4-1. データの調整 - Annexコンテンツのバリアントファイルのデータ調整
    """
    pass

def prepare_sync():
    """4-2. 同期の準備
    """
    pass


RF_FORM_FILE = os.path.join(path.RF_FORM_DATA_DIR, 'conflict_helper.json')


def exist_rf_form_file()->bool:
    """Check for the existence of the conflict_helper.json file

    Returns:
        [bool]: [True : exist, False : no exist]
    """
    return os.path.exists(RF_FORM_FILE)


def trans_top():
    """Display a link button to the Study or Execution Flow Top Page.

    1. In the research execution environment, it is displayed as a link button on the research flow top page.
    2. In the experiment execution environment, it is displayed as a link button on the top page of the experiment flow.
    """

    # Identify whether the function execution environment is research or experimental
    # If the ex_pkg_info.json file is not present, the research execution environment, and if present, the experimental execution environment.

    html_text = ''
    if epi.exist_file():
        # For experiment execution environment
        top_path = os.path.join('./../', path.EXPERIMENT_DIR ,path.EXPERIMENT_TOP)
        html_text = pd.button_html(top_path, message.get("menu", "trans_experiment_top"))
    else:
        # For research execution environment
        top_path = os.path.join('./../', path.RESEARCH_DIR ,path.RESEARCH_TOP)
        html_text = pd.button_html(top_path, message.get("menu", "trans_reserch_top"))
    display(HTML(html_text))


def divide_rf_notebook_or_non_file(filepaths : list[str]) -> tuple[list[str], list[str]]:
    """Method to separate DG RF Notebook files from non-DG RF Notebook files with a given file path list

    Args:
        filepaths (list[str]): [target file path list]

    Returns:
        tuple[list[str], list[str]]: [The first return value is the RF Notebook file path list, the second is any other file path list.]
    """

    rf_notebook_filepaths = list[str]()
    non_rf_notebook_filepaths = list[str]()
    for path in filepaths:
        if is_rf_notebook(path):
            # only auto-resolve content path
            rf_notebook_filepaths.append(path)
        else:
            #  only custom-resolve content path by user
            non_rf_notebook_filepaths.append(path)
    return rf_notebook_filepaths, non_rf_notebook_filepaths

def is_rf_notebook(filepath : str)->bool:
    """Method to determine if the given file path is a DG RF Notebook file

    Args:
        filepath (str): [target file path]

    Returns:
        bool: [True : target file path is RF notebook, False : target file path is not RF notebook]
    """
    return '.ipynb' in filepath and not (filepath.startswith('experiments/'))

def save_task_notebooks_to_tmp(filepaths : list):
    for path in filepaths:
        copy_local_content_to_tmp(path)

def copy_local_content_to_tmp(target_path:str):
    """Copy locale version contents under .tmp/conflict

    Args:
        target_path (str): [destination file path]
    """
    hash = git.get_local_object_hash_by_path(target_path)
    to_copy_file_path = os.path.join(path.TMP_CONFLICT_DIR, target_path)
    target_dir_path = os.path.dirname(to_copy_file_path)
    os.makedirs(target_dir_path, exist_ok=True)
    os.system('git cat-file -p {} > {}'.format(hash, to_copy_file_path))

RF_DATA_FILE_PATH = os.path.join(path.RF_FORM_DATA_DIR, 'conflict_helper.json')

def record_rf_data_conflict_info(
        git_conflict_file_path_list, git_auto_conflict_filepaths, git_custom_conflict_filepaths, annex_conflict_file_path_list):

    rf_data = {
        'conflict_files' : {
            'git' : {
                'all' : git_conflict_file_path_list,
                'auto' : git_auto_conflict_filepaths,
                'user' : git_custom_conflict_filepaths
            },
            'annex' : annex_conflict_file_path_list
        }
    }
    os.makedirs(path.RF_FORM_DATA_DIR, exist_ok=True)
    fo.write_to_json(RF_DATA_FILE_PATH, rf_data)
