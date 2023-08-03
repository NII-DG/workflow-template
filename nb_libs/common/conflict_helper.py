import json
import os
import traceback
from ..utils.params import ex_pkg_info as epi
from ..utils.path import path, display as pd
from ..utils.message import message, display as md
from ..utils.git import git_module as git
from ..utils.common import common
from ..utils.except_class import DGTaskError, NotFoundKey, FoundUnnecessarykey
from IPython.display import HTML, display
from datalad import api
import panel as pn



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
        md.display_debug(f'[DEBUG] git_conflict_file_path_list : {git_conflict_file_path_list}')
        md.display_debug(f'[DEBUG] git_auto_conflict_filepaths : {git_auto_conflict_filepaths}')
        md.display_debug(f'[DEBUG] git_custom_conflict_filepaths : {git_custom_conflict_filepaths}')
        md.display_debug(f'[DEBUG] annex_conflict_file_path_list : {annex_conflict_file_path_list}')

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
    # Execution availability check
    ## get rf data
    try:
        rf_data = get_rf_data()
        need_key = [KEY_CONFLICT_FILES]
        no_need_key = [KEY_ANNEX_CONFLICT_PREPARE_INFO]
        check_key_rf_data(rf_data, need_key, no_need_key)

    except FileNotFoundError as e:
        err_msg = message.get('nb_exec', 'not_exec_pre_section')
        md.display_err(err_msg)
        raise DGTaskError() from e

    except FoundUnnecessarykey as e:
        err_msg = message.get('conflict_helper', 'non_already_done').format(message.get('conflict_helper','get_annex_variatns'))
        md.display_err(err_msg)
        raise DGTaskError() from e

    except NotFoundKey as e:
        err_msg = message.get('DEFAULT', 'unexpected')
        md.display_err(err_msg)
        raise DGTaskError() from e

    # Get conflicted annex paths
    try:
        conflicted_annex_paths = get_conflicted_annex_paths_from_rf_data(rf_data)
        md.display_debug(f'[DEBUG] conflicted_annex_paths : {conflicted_annex_paths}')
        md.display_debug(f'[DEBUG] len(conflicted_annex_paths) : {len(conflicted_annex_paths)}')
        if len(conflicted_annex_paths) > 0:
            annex_rslv_info = get_annex_rslv_info(conflicted_annex_paths)
            md.display_debug(f'[DEBUG] annex_rslv_info \n : {json.dumps(annex_rslv_info, indent=4)}')
            dl_data_remote_variatns(annex_rslv_info)
            record_rf_data_annex_rslv_info(rf_data, annex_rslv_info)
            ## Prompts operation of the next section
            msg = message.get('conflict_helper', 'finish_get_annex_variatns_done')
            md.display_info(msg)
            return

        else:
            record_rf_data_annex_rslv_info(rf_data)
            ## Prompts operation of the next section
            msg = message.get('conflict_helper', 'finish_get_annex_variatns_no_done')
            md.display_info(msg)
            return

    except Exception as e:
        err_msg = message.get('nb_exec', 'not_exec_pre_section')
        md.display_err(err_msg)
        raise DGTaskError() from e

def record_preparing_event_for_resolving_conflict():
    """2-2. 競合解消準備をリポジトリ履歴に記録
    """
    # Execution availability check
    ## get rf data
    try:
        rf_data = get_rf_data()
        need_key = [KEY_CONFLICT_FILES, KEY_ANNEX_CONFLICT_PREPARE_INFO]
        no_need_key = [KEY_IS_PREPARE]
        check_key_rf_data(rf_data, need_key, no_need_key)

    except FileNotFoundError as e:
        err_msg = message.get('nb_exec', 'not_exec_pre_section')
        md.display_err(err_msg)
        raise DGTaskError() from e

    except FoundUnnecessarykey as e:
        err_msg = message.get('conflict_helper', 'non_already_done').format(message.get('conflict_helper','record_preparing_event_for_resolving_conflict'))
        md.display_err(err_msg)
        raise DGTaskError() from e

    except NotFoundKey as e:
        except_msg = traceback.format_exception_only(type(e), e)
        if KEY_CONFLICT_FILES in except_msg:
            err_msg = message.get('DEFAULT', 'unexpected')
            md.display_err(err_msg)
        elif KEY_ANNEX_CONFLICT_PREPARE_INFO in except_msg:
            err_msg = message.get('nb_exec', 'not_exec_pre_section')
            md.display_err(err_msg)
        raise DGTaskError() from e

    except Exception as e:
        err_msg = message.get('DEFAULT', 'unexpected')
        md.display_err(err_msg)
        raise DGTaskError() from e


    try:
        # 「競合Gitファイルパスリスト」と「競合Annexファイルパスリスト」がそれぞれ1以上の場合に以下の処理をする。
        git_conflict_filepaths, annex_conflict_paths = get_conflicted_git_annex_paths_from_rf_data(rf_data)

        for git_path in git_conflict_filepaths:
            if not git_path.startswith(path.HOME_PATH):
                git_path = os.path.join(path.HOME_PATH, git_path)
            md.display_debug(f'[DEBUG] git add. git_path : {git_path}')
            git.git_add(git_path)

        # set commit msg
        commit_msg = ''
        if len(git_conflict_filepaths) >0 and len(annex_conflict_paths) >0:
            commit_msg = 'Resolvemerge Result(git and git-annex)'
        elif len(git_conflict_filepaths) > 0:
            commit_msg = 'Resolvemerge Result(git)'
        elif len(annex_conflict_paths) >0:
            commit_msg = 'Resolvemerge Result(git-annex)'
        else:
            err_msg = message.get('DEFAULT', 'unexpected')
            md.display_err(err_msg)
            raise DGTaskError('Unexpected error: there is an abnormality in the file path list of the conflicting Git or Annex.')

        md.display_debug(f'[DEBUG] commit_msg  : {commit_msg}')
        git.git_annex_lock(path.HOME_PATH)
        git.git_commmit(commit_msg)
        git.git_annex_unlock(path.HOME_PATH)

        ## updata rf_data
        record_rf_data_is_prepare(rf_data)

    except Exception as e:
        err_msg = message.get('DEFAULT', 'unexpected')
        md.display_err(err_msg)
        raise DGTaskError() from e

    else:
        ## Prompts operation of the next section
        msg = message.get('conflict_helper', 'finish_record_preparing_event_for_resolving_conflict')
        md.display_info(msg)
        return


def resolving_git_content():
    """3-1. gitコンテンツの競合解消
    """
    # Execution availability check
    ## get rf data
    try:
        rf_data = get_rf_data()
        need_key = [KEY_CONFLICT_FILES, KEY_ANNEX_CONFLICT_PREPARE_INFO, KEY_IS_PREPARE]
        no_need_key = []
        check_key_rf_data(rf_data, need_key, no_need_key)
    except FileNotFoundError as e:
        err_msg = message.get('nb_exec', 'not_exec_pre_section')
        md.display_err(err_msg)
        raise DGTaskError() from e

    except NotFoundKey as e:
        except_msg = traceback.format_exception_only(type(e), e)
        if KEY_CONFLICT_FILES in except_msg:
            err_msg = message.get('DEFAULT', 'unexpected')
            md.display_err(err_msg)
        elif KEY_ANNEX_CONFLICT_PREPARE_INFO in except_msg or KEY_IS_PREPARE in except_msg:
            err_msg = message.get('nb_exec', 'not_exec_pre_section')
            md.display_err(err_msg)
        raise DGTaskError() from e

    except Exception as e:
        err_msg = message.get('DEFAULT', 'unexpected')
        md.display_err(err_msg)
        raise DGTaskError() from e

    # get user resolving conflicted git paths from rf_data
    conflicted_git_path = get_user_custom_conflicted_git_paths_from_rf_data(rf_data)

    # Check path number
    if len(conflicted_git_path) > 0:
        # display conflict resolve form
        git_conflict_resolve_form(conflicted_git_path)

    else:
        record_rf_data_resolving_git(rf_data)
        # no need doing section
        msg = message.get('conflict_helper', 'no_need_exec_cell').format(message.get('conflict_helper', 'resolving_git_content'))
        md.display_err(msg)
        return





def select_action_for_resolving_annex():
    """3-2. Annexコンテンツの競合解消アクションを選択
    """
    # Execution availability check
    ## get rf data
    try:
        rf_data = get_rf_data()
        need_key = [KEY_CONFLICT_FILES, KEY_ANNEX_CONFLICT_PREPARE_INFO, KEY_IS_PREPARE, KEY_RESOLVING_GIT]
        no_need_key = []
        check_key_rf_data(rf_data, need_key, no_need_key)

    except FileNotFoundError as e:
        err_msg = message.get('nb_exec', 'not_exec_pre_section')
        md.display_err(err_msg)
        raise DGTaskError() from e

    except NotFoundKey as e:
        except_msg = traceback.format_exception_only(type(e), e)
        if KEY_CONFLICT_FILES in except_msg:
            err_msg = message.get('DEFAULT', 'unexpected')
            md.display_err(err_msg)
        elif KEY_ANNEX_CONFLICT_PREPARE_INFO in except_msg or KEY_IS_PREPARE in except_msg or KEY_RESOLVING_GIT in except_msg:
            err_msg = message.get('nb_exec', 'not_exec_pre_section')
            md.display_err(err_msg)
        raise DGTaskError() from e

    except Exception as e:
        err_msg = message.get('DEFAULT', 'unexpected')
        md.display_err(err_msg)
        raise DGTaskError() from e

    # get user resolving conflicted annex paths from rf_data
    conflicted_annex_path = get_conflicted_annex_paths_from_rf_data(rf_data=rf_data)
    prepare_info = rf_data.get(KEY_ANNEX_CONFLICT_PREPARE_INFO)


    # Check path number
    if len(conflicted_annex_path) > 0 and prepare_info != None:
        # display conflict resolve form
        annex_conflict_resolve_action_form(rf_data)
    elif len(conflicted_annex_path) > 0 and prepare_info == None:
        msg = message.get('nb_exec', 'not_exec_pre_section')
        md.display_err(msg)
        return
    elif len(conflicted_annex_path) <= 0 and prepare_info != None:
        msg = message.get('DEFAULT', 'unexpected_errors_format').format('競合の解析情報が異常です')
        md.display_err(msg)
        return
    else:
        record_rf_data_annex_selected_action(rf_data=rf_data)
        # no need doing section
        msg = message.get('conflict_helper', 'no_need_exec_cell').format(message.get('conflict_helper', 'select_action_for_resolving_annex'))
        md.display_info(msg)
        return

def rename_variants():
    """3-3. ≪両方を残す≫を選択したファイル名の入力
    """
        # Execution availability check
    ## get rf data
    try:
        rf_data = get_rf_data()
        need_key = [KEY_CONFLICT_FILES, KEY_ANNEX_CONFLICT_PREPARE_INFO, KEY_IS_PREPARE, KEY_RESOLVING_GIT, KEY_ANNEX_SELECTED_ACTION]
        no_need_key = []
        check_key_rf_data(rf_data, need_key, no_need_key)

    except FileNotFoundError as e:
        err_msg = message.get('nb_exec', 'not_exec_pre_section')
        md.display_err(err_msg)
        raise DGTaskError() from e

    except NotFoundKey as e:
        except_msg = traceback.format_exception_only(type(e), e)
        if KEY_CONFLICT_FILES in except_msg:
            err_msg = message.get('DEFAULT', 'unexpected')
            md.display_err(err_msg)
        elif KEY_ANNEX_CONFLICT_PREPARE_INFO in except_msg or KEY_IS_PREPARE in except_msg or KEY_RESOLVING_GIT in except_msg or KEY_ANNEX_SELECTED_ACTION in except_msg:
            err_msg = message.get('nb_exec', 'not_exec_pre_section')
            md.display_err(err_msg)
        raise DGTaskError() from e

    except Exception as e:
        err_msg = message.get('DEFAULT', 'unexpected')
        md.display_err(err_msg)
        raise DGTaskError() from e

    annex_selectef_action = rf_data[KEY_ANNEX_SELECTED_ACTION]

    both_annex_path = list()

    if annex_selectef_action is None:
        # not need operate cell
        msg = message.get('conflict_helper','no_need_exec_cell').format(message.get('conflict_helper','rename_variants'))
        md.display_info(msg)
        return
    else:
        # get annex path selected both
        for key, val in annex_selectef_action.item():
            action_type = val['action']
            if action_type == BOTH_REMAIN:
                both_annex_path.append(key)

    if len(both_annex_path) <= 0:
        # not need operate cell
        msg = message.get('conflict_helper','no_need_exec_cell').format(message.get('conflict_helper','rename_variants'))
        md.display_info(msg)
        return

    # NEED operate cell for form



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

def get_annex_rslv_info(conflicted_annex_paths):
    annex_rslv_info = dict[str, dict]()
    git.git_annex_resolvemerge()
    unique_dir_path = common.get_AND_dirpaths(conflicted_annex_paths)
    candidate_varitan_file_list = api.status(path=unique_dir_path)

    for candidate_file in candidate_varitan_file_list:

        for conflict_annex_path in conflicted_annex_paths:
            # adjust file path that is conflicted for extract variant path
            dirpath = os.path.dirname(conflict_annex_path)
            filename_no_extension = os.path.splitext(os.path.basename(conflict_annex_path))[0]
            target_path = '{}/{}.variant-'.format(dirpath, filename_no_extension)

            candidate_file_path = candidate_file['path']
            refds = '{}/'.format(candidate_file['refds'])
            candidate_file_path = candidate_file_path.replace(refds, '', 1)

            if candidate_file_path.startswith(target_path) and equal_extension(conflict_annex_path, candidate_file_path) :
                variant_list = dict[str, str]()
                abs_candidate_file_path = os.path.join(path.HOME_PATH, candidate_file_path)
                if os.path.isfile(abs_candidate_file_path):
                    variant_list['local'] =  candidate_file_path
                else:
                    variant_list['remote'] =  candidate_file_path
                annex_rslv_info[conflict_annex_path] = variant_list
    return annex_rslv_info

def dl_data_remote_variatns(annex_rslv_info:dict):
    to_datalad_get_paths = []
    for v in annex_rslv_info.values():
        to_datalad_get_paths.append(
            os.path.join(path.HOME_PATH,v['remote'])
            )
    if len(to_datalad_get_paths) > 0:
        api.get(path=to_datalad_get_paths)

def equal_extension(base_file_path, variant_file_path):
    return (get_extension_for_varinat(variant_file_path) == get_extension_for_varinat(base_file_path))

def get_extension_for_varinat(path):
    extension = os.path.splitext(os.path.basename(path))[1]
    if 'variant-' in extension:
        return ''
    return extension

"""
conflict_helper.json操作群
"""

RF_DATA_FILE_PATH = os.path.join(path.RF_FORM_DATA_DIR, 'conflict_helper.json')
KEY_CONFLICT_FILES = 'conflict_files'
KEY_GIT = 'git'
KEY_GIT_ALL = 'all'
KEY_GIT_AUTO = 'auto'
KEY_GIT_USER = 'user'
KEY_ANNEX = 'annex'
KEY_ANNEX_CONFLICT_PREPARE_INFO = 'annex_conflict_prepare_info'
KEY_IS_PREPARE = 'is_prepare'
KEY_RESOLVING_GIT = 'resolving_git'
KEY_ACTION = 'action'
KEY_ANNEX_SELECTED_ACTION = 'annex_selected_action'

def record_rf_data_conflict_info(
        git_conflict_file_path_list, git_auto_conflict_filepaths, git_custom_conflict_filepaths, annex_conflict_file_path_list):

    rf_data = {
        KEY_CONFLICT_FILES : {
            KEY_GIT : {
                KEY_GIT_ALL : git_conflict_file_path_list,
                KEY_GIT_AUTO : git_auto_conflict_filepaths,
                KEY_GIT_USER : git_custom_conflict_filepaths
            },
            KEY_ANNEX : annex_conflict_file_path_list
        }
    }
    os.makedirs(path.TMP_DIR, exist_ok=True)
    os.makedirs(path.RF_FORM_DATA_DIR, exist_ok=True)
    common.create_json_file(RF_DATA_FILE_PATH, rf_data)

def record_rf_data_annex_rslv_info(rf_data=None, annex_rslv_info=None):
    if rf_data == None:
        rf_data = get_rf_data()
    rf_data[KEY_ANNEX_CONFLICT_PREPARE_INFO] = annex_rslv_info
    common.create_json_file(RF_DATA_FILE_PATH, rf_data)

def record_rf_data_is_prepare(rf_data=None):
    if rf_data == None:
        rf_data = get_rf_data()
    rf_data[KEY_IS_PREPARE] = True
    common.create_json_file(RF_DATA_FILE_PATH, rf_data)

def record_rf_data_resolving_git(rf_data=None):
    if rf_data == None:
        rf_data = get_rf_data()
    rf_data[KEY_RESOLVING_GIT] = True
    common.create_json_file(RF_DATA_FILE_PATH, rf_data)

def record_rf_data_annex_selected_action(value=None, rf_data=None,):
    if rf_data == None:
        rf_data = get_rf_data()
    rf_data[KEY_ANNEX_SELECTED_ACTION] = value
    common.create_json_file(RF_DATA_FILE_PATH, rf_data)



def get_rf_data()->dict:
    return common.read_json_file(RF_DATA_FILE_PATH)

def get_conflicted_annex_paths_from_rf_data(rf_data: dict):
    return rf_data[KEY_CONFLICT_FILES][KEY_ANNEX]

def get_user_custom_conflicted_git_paths_from_rf_data(rf_data: dict):
    return rf_data[KEY_CONFLICT_FILES][KEY_GIT][KEY_GIT_USER]

def get_conflicted_git_paths_from_rf_data(rf_data: dict):
    return rf_data[KEY_CONFLICT_FILES][KEY_GIT][KEY_GIT_ALL]

def get_annex_rslv_info_from_rf_data(rf_data: dict)->dict:
    return rf_data[KEY_ANNEX_CONFLICT_PREPARE_INFO]

def get_conflicted_git_annex_paths_from_rf_data(rf_data: dict):
    return get_conflicted_git_paths_from_rf_data(rf_data), get_conflicted_annex_paths_from_rf_data(rf_data)


def check_key_rf_data(rf_data: dict, need_key, no_need_key :list):
    keys = rf_data.keys()

    for key in keys:
        if key not in need_key:
            raise NotFoundKey('Required key is included in the data. KEY[{}]'.format(key))
        if key in no_need_key:
            raise FoundUnnecessarykey('Unnecessary key is included in the data. KEY[{}]'.format(key))


"""
FORM CLASS
"""
git_conflict_rslv_form_whole_msg = pn.pane.HTML()

class GitFileResolveForm:
    """3-1. gitコンテンツの競合解消のフォームクラス
    """
    def __init__(self, index, target_file_path:str, all_paths:list):
        self.file_path = target_file_path
        self.all_paths = all_paths

        self.confirm_button = pn.widgets.Button(name=message.get('conflict_helper', 'correction_complete'), button_type='default')
        self.confirm_button.on_click(self.confirm_resolve)
        self.confirm_button.width = 200

        title = f'{index}：{self.file_path}'
        link = f'../../../../edit/{self.file_path}'
        link_html = pd.create_link(url=link, title=title)
        self.label = pn.pane.HTML(link_html)

    def confirm_resolve(self, event):
        try:
            modified_files = git.get_modified_filepaths()
            # Confirm that the file has been edited
            if self.file_path in modified_files:
                self.confirm_button.button_type = 'success'
                self.confirm_button.name = message.get('conflict_helper', 'correction_complete')
            else:
                self.confirm_button.button_type = 'danger'
                self.confirm_button.name = message.get('conflict_helper', 'correction_imcomplete')

            # Check the status of all edits
            if is_correction_complete(self.all_paths, modified_files):
                msg=message.get('conflict_helper','all_correction_complete')
                git_conflict_rslv_form_whole_msg.object = md.creat_html_msg_info_p(msg=msg)
                # update conflict_helper.json
                record_rf_data_resolving_git()

        except Exception as e:
            err_msg=message.get('DEFAULT','unexpected_errors_format').format(str(e))
            git_conflict_rslv_form_whole_msg.object = md.creat_html_msg_err_p(msg=err_msg)


def git_conflict_resolve_form(file_paths):
    pn.extension()
    form_items = []
    for index, file_path in enumerate(common.sortFilePath(file_paths)):
        pair = GitFileResolveForm(index, file_path, file_paths)
        form_items.append(pn.Column(pair.label,pair.confirm_button))
    git_conflict_rslv_form_whole_msg.object = ''
    git_conflict_rslv_form_whole_msg.width = 900
    if is_correction_complete(file_paths):
        msg=message.get('conflict_helper','already_all_correction_complete')
        git_conflict_rslv_form_whole_msg.object = md.creat_html_msg_info_p(msg=msg)
        record_rf_data_resolving_git()

    display(pn.Column(*form_items, git_conflict_rslv_form_whole_msg))

def is_correction_complete(target_paths, modified_files=None)->bool:
    if modified_files == None:
        modified_files = git.get_modified_filepaths()
    now_target_modified_files = common.get_AND_elements(target_paths, modified_files)
    return len(target_paths) == len(now_target_modified_files)



"""
Annexアクション選択フォーム
"""
annex_action_form_whole_msg = pn.pane.HTML()

DEFUALT = 'default'
LOCAL_REMAIN = 'local'
REMOTE_REMAIN = 'remote'
BOTH_REMAIN = 'both'

class AnnexFileActionForm:
    """3-1. gitコンテンツの競合解消アクションフォームクラス
    """
    def __init__(self, rf_data:dict):
        # set rf_data
        self.rf_data = rf_data
        # set confirm_button
        self.confirm_button = pn.widgets.Button(name=message.get('conflict_helper', 'action_confirmed'), button_type='default')
        self.confirm_button.on_click(self.submit)
        top_col = pn.Column()
        # get file list
        annex_rslv_info = get_annex_rslv_info_from_rf_data(self.rf_data)
        filepaths = common.sortFilePath(list(annex_rslv_info.keys()))

        options = dict()
        options[message.get('conflict_helper', 'defualt')] = DEFUALT
        options[message.get('conflict_helper', 'local_remain')] = LOCAL_REMAIN
        options[message.get('conflict_helper', 'remote_remain')] = REMOTE_REMAIN
        options[message.get('conflict_helper', 'both_remain')] = BOTH_REMAIN
        # set options
        self.options = options
        # set file_col_num
        self.file_col_num = len(filepaths)

        # set top_col
        self.top_col_data = list()
        for index, filepath in enumerate(filepaths):
            local_remote = annex_rslv_info[filepath]
            base_file = pn.widgets.StaticText(name=str(index), value=filepath)

            local_path = local_remote['local']
            local_url = f'../../../../edit/{local_path}'
            local_link_html = pd.create_link(url=local_url, title=message.get('conflict_helper','local_variant'))
            local_link = pn.pane.HTML(local_link_html)

            remote_path = local_remote['remote']
            remoto_url = f'../../../../edit/{remote_path}'
            remoto_link_html = pd.create_link(url=remoto_url, title=message.get('conflict_helper','remote_variant'))
            remoto_link = pn.pane.HTML(remoto_link_html)
            head_data = [base_file, local_link, remoto_link]

            selector = pn.widgets.Select(options=self.options)
            file_col_data = [head_data, selector]
            self.top_col_data.append(file_col_data)

    def submit(self, event):
        try:
            top_col = self.top_col_data
            file_clo_num = self.file_col_num

            annex_selected_action = dict()

            for i in range(file_clo_num):

                selected_key = top_col[i][0].value
                selected_value = self.options[selected_key]

                if selected_value == DEFUALT:
                    # DEFUALT値が選ばれたら選択エラー、再度入力
                    self.confirm_button.button_type = 'danger'
                    self.confirm_button.name = message.get('conflict_helper', 'select_default_error')
                    return

                base_file_path = top_col[i][0][0].value
                annex_selected_action[base_file_path] = {'action' : selected_value}

            # update conflict_helper.json
            record_rf_data_annex_selected_action(value=annex_selected_action, rf_data=self.rf_data)
            self.confirm_button.button_type = 'success'
            self.confirm_button.name = message.get('conflict_helper', 'complete_action')
            return
        except Exception as e:
            self.confirm_button.button_type = 'danger'
            self.confirm_button.name = message.get('DEFAULT', 'unexpected')
            err_msg=message.get('DEFAULT','unexpected_errors_format').format(str(e))
            annex_action_form_whole_msg.object = md.creat_html_msg_err_p(msg=err_msg)


def annex_conflict_resolve_action_form(rf_data:dict):
    pn.extension()
    form = AnnexFileActionForm(rf_data)
    annex_action_form_whole_msg.object = ''
    annex_action_form_whole_msg.width = 900
    top_col = pn.Column()
    for file_col_data in form.top_col_data:
        head_data = file_col_data[0]
        head = pn.Row(*head_data)
        selector = file_col_data[1]
        file_col = pn.Column(head, selector)
        top_col.append(file_col)


    display(pn.Column(top_col, form.confirm_button ,annex_action_form_whole_msg))
