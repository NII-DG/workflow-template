import json
import os
import shutil
import traceback
from ..utils.params import ex_pkg_info as epi
from ..utils.path import path, display as pd
from ..utils.message import message, display as md
from ..utils.git import git_module as git
from ..utils.common import common, raise_error
from ..utils.except_class import DGTaskError, NotFoundKey, FoundUnnecessarykey
from IPython.display import HTML, display, clear_output
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
        need_key = []
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

    except Exception as e:
        err_msg = message.get('DEFAULT', 'unexpected')
        md.display_err(err_msg)
        raise DGTaskError() from e

    # Get conflicted annex paths
    try:
        conflicted_annex_paths = get_conflicted_annex_paths_from_rf_data(rf_data)
        if len(conflicted_annex_paths) > 0:
            annex_rslv_info = get_annex_rslv_info(conflicted_annex_paths)
            dl_data_remote_variatns(annex_rslv_info)
            record_rf_data_annex_rslv_info(rf_data, annex_rslv_info)
            ## Prompts operation of the next section
            msg = message.get('conflict_helper', 'finish_get_annex_variatns_done')
            clear_output()
            md.display_info(msg)
            return

        else:
            record_rf_data_annex_rslv_info(rf_data)
            ## Prompts operation of the next section
            msg = message.get('conflict_helper', 'finish_get_annex_variatns_no_done')
            clear_output()
            md.display_info(msg)
            return

    except Exception as e:
        err_msg = message.get('DEFAULT', 'unexpected')
        md.display_err(err_msg)
        raise DGTaskError() from e

def record_preparing_event_for_resolving_conflict():
    """2-2. 競合解消準備をリポジトリ履歴に記録
    """
    # Execution availability check
    ## get rf data
    try:
        rf_data = get_rf_data()
        need_key = [KEY_ANNEX_CONFLICT_PREPARE_INFO]
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
        need_key = [KEY_IS_PREPARE]
        no_need_key = []
        check_key_rf_data(rf_data, need_key, no_need_key)
    except FileNotFoundError as e:
        err_msg = message.get('nb_exec', 'not_exec_pre_section')
        md.display_err(err_msg)
        return
    except NotFoundKey as e:
        err_msg = message.get('nb_exec', 'not_exec_pre_section')
        md.display_err(err_msg)
        return
    except Exception as e:
        err_msg = message.get('DEFAULT', 'unexpected')
        md.display_err(err_msg)
        raise DGTaskError() from e
    else:
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
            md.display_info(msg)
            return





def select_action_for_resolving_annex():
    """3-2. Annexコンテンツの競合解消アクションを選択
    """
    # Execution availability check
    ## get rf data
    try:
        rf_data = get_rf_data()
        need_key = [KEY_RESOLVING_GIT]
        no_need_key = [KEY_FIXATION]
        check_key_rf_data(rf_data, need_key, no_need_key)

    except FileNotFoundError as e:
        err_msg = message.get('nb_exec', 'not_exec_pre_section')
        md.display_err(err_msg)
        return

    except NotFoundKey as e:
        err_msg = message.get('nb_exec', 'not_exec_pre_section')
        md.display_err(err_msg)
        return

    except FoundUnnecessarykey as e:
        err_msg = message.get('conflict_helper', 'input_fixation')
        md.display_err(err_msg)
        return

    except Exception as e:
        err_msg = message.get('DEFAULT', 'unexpected')
        md.display_err(err_msg)
        raise DGTaskError() from e
    else:
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
        need_key = [KEY_ANNEX_SELECTED_ACTION]
        no_need_key = [KEY_FIXATION]
        check_key_rf_data(rf_data, need_key, no_need_key)

    except FileNotFoundError as e:
        err_msg = message.get('nb_exec', 'not_exec_pre_section')
        md.display_err(err_msg)
        return

    except NotFoundKey as e:
        err_msg = message.get('nb_exec', 'not_exec_pre_section')
        md.display_err(err_msg)
        return

    except FoundUnnecessarykey as e:
        err_msg = message.get('conflict_helper', 'input_fixation')
        md.display_err(err_msg)
        return

    except Exception as e:
        err_msg = message.get('DEFAULT', 'unexpected')
        md.display_err(err_msg)
        raise DGTaskError() from e
    else:
        annex_selectef_action = rf_data[KEY_ANNEX_SELECTED_ACTION]

        both_annex_path = list()

        if annex_selectef_action is None:
            # not need operate cell
            msg = message.get('conflict_helper','no_need_exec_cell').format(message.get('conflict_helper','rename_variants'))
            md.display_info(msg)
            return
        else:
            # get annex path selected both
            for key, val in annex_selectef_action.items():
                action_type = val['action']
                if action_type == BOTH_REMAIN:
                    both_annex_path.append(key)

        if len(both_annex_path) <= 0:
            # not need operate cell
            msg = message.get('conflict_helper','no_need_exec_cell').format(message.get('conflict_helper','rename_variants'))
            md.display_info(msg)
            return

        # NEED operate cell for form
        annex_conflict_resolve_rename_form(rf_data=rf_data, both_rename_list=both_annex_path)




def auto_resolve_task_notebooks()->bool:
    """4-1. データの調整 - タスクNotebookの自動解消
    """
    # Execution availability check
    ## get rf data
    try:
        rf_data = get_rf_data()
        need_key = [KEY_RESOLVING_GIT, KEY_ANNEX_SELECTED_ACTION]
        no_need_key = []
        check_key_rf_data(rf_data, need_key, no_need_key)

    except FileNotFoundError as e:
        err_msg = message.get('nb_exec', 'not_exec_pre_section')
        md.display_err(err_msg)
        raise DGTaskError() from e

    except NotFoundKey as e:
        err_msg = message.get('nb_exec', 'not_exec_pre_section')
        md.display_err(err_msg)
        raise DGTaskError() from e

    except Exception as e:
        err_msg = message.get('DEFAULT', 'unexpected')
        md.display_err(err_msg)
        raise DGTaskError() from e

    ## rf_data[annex_selected_action]の中を検査する。
    if rf_data[KEY_ANNEX_SELECTED_ACTION] is not None:
        annex_selected_action = rf_data[KEY_ANNEX_SELECTED_ACTION]
        ## 両ファイルを残す選択データに対して、リネーム値が設定されていなければエラー
        for value in annex_selected_action.values():
            if value[KEY_ACTION] == BOTH_REMAIN:
                local_name = value.get(KEY_LOCAL_NAME)
                remote_name = value.get(KEY_REMOTE_NAME)
                if local_name is None and remote_name is None:
                    err_msg = message.get('nb_exec', 'not_exec_pre_section')
                    md.display_err(err_msg)
                    raise DGTaskError('Not Found Both Rename Values')
                elif (local_name is None and remote_name is not None):
                    err_msg = message.get('DEFAULT', 'unexpected')
                    md.display_err(err_msg)
                    raise DGTaskError('Not Found Only REMOTE Rename Values')
                elif (local_name is not None and remote_name is None):
                    err_msg = message.get('DEFAULT', 'unexpected')
                    md.display_err(err_msg)
                    raise DGTaskError('Not Found Only LOCAL Rename Values')
                else:
                    continue

    # conflict_helper.jsonから「競合自動回復Gitファイルパス」を取得する。
    auto_resolve_paths = rf_data[KEY_CONFLICT_FILES][KEY_GIT][KEY_GIT_AUTO]
    if len(auto_resolve_paths)>0:
        save_task_notebooks_to_repo_from_tmp(auto_resolve_paths)
        del_tmp_task_notebooks()
        # これまでの入力を固定するためのフラグを付与する。
        record_rf_data_fixation(rf_data)
        msg = message.get('conflict_helper', 'complete_adjust_task_notebook')
        md.display_info(msg)
        return True
    else:
        # これまでの入力を固定するためのフラグを付与する。
        record_rf_data_fixation(rf_data)
        msg = message.get('conflict_helper', 'no_need_adjust_task_notebook')
        md.display_info(msg)
        return True


def adjust_annex_data()->tuple[list[str],list[str]]:
    """4-1. データの調整 - Annexコンテンツのバリアントファイルのデータ調整
    """
    ## get rf data
    try:
        rf_data = get_rf_data()
    except Exception as e:
        err_msg = message.get('DEFAULT', 'unexpected')
        md.display_err(err_msg)
        raise DGTaskError() from e

    # 競合Annexファイルパスリストを取得する
    annex_conflict_paths = rf_data[KEY_CONFLICT_FILES][KEY_ANNEX]
    if len(annex_conflict_paths)>0:
        ## Annex選択アクション情報を取得
        annex_selected_action = rf_data[KEY_ANNEX_SELECTED_ACTION]
        ## Annex競合解消準備情報を取得
        annex_prepare_info = rf_data[KEY_ANNEX_CONFLICT_PREPARE_INFO]
        path_after_rename_list = list()
        delete_file_path_list = list()
        for conflict_annex_path, info in annex_selected_action.items():
            # アクション種別を取得
            action_type = info[KEY_ACTION]
            if action_type == BOTH_REMAIN:
                # ローカルバリアントリネーム
                local_rename = info[KEY_LOCAL_NAME]
                local_variant_filepath = annex_prepare_info[conflict_annex_path][KEY_LOCAL]
                local_path_after_rename = rename_file(base_filepath=local_variant_filepath, future_name=local_rename)
                path_after_rename_list.append(local_path_after_rename)
                # リモートバリアントリネーム
                remote_rename = info[KEY_REMOTE_NAME]
                remote_variant_filepath = annex_prepare_info[conflict_annex_path][KEY_REMOTE]
                remote_path_after_rename = rename_file(base_filepath=remote_variant_filepath, future_name=remote_rename)
                path_after_rename_list.append(remote_path_after_rename)
            elif action_type == LOCAL_REMAIN:
                # ローカルバリアントリネーム
                local_rename = os.path.basename(conflict_annex_path)
                local_variant_filepath = annex_prepare_info[conflict_annex_path][KEY_LOCAL]
                path_after_rename = rename_file(base_filepath=local_variant_filepath,future_name=local_rename)
                path_after_rename_list.append(path_after_rename)
                # リモートバリアント削除
                remote_variant_filepath = annex_prepare_info[conflict_annex_path][KEY_REMOTE]
                common.delete_file(file_path=os.path.join(path.HOME_PATH, remote_variant_filepath), raise_err=True)
                delete_file_path_list.append(remote_variant_filepath)
            elif action_type == REMOTE_REMAIN:
                # リモートバリアントリネーム
                remote_rename = os.path.basename(conflict_annex_path)
                remote_variant_filepath = annex_prepare_info[conflict_annex_path][KEY_REMOTE]
                path_after_rename = rename_file(base_filepath=remote_variant_filepath, future_name=remote_rename)
                path_after_rename_list.append(path_after_rename)
                # ローカルバリアント削除
                local_variant_filepath = annex_prepare_info[conflict_annex_path][KEY_LOCAL]
                common.delete_file(file_path=os.path.join(path.HOME_PATH, local_variant_filepath), raise_err=True)
                delete_file_path_list.append(local_variant_filepath)
            else:
                err_msg = message.get('DEFAULT', 'unexpected')
                md.display_err(err_msg)
                raise DGTaskError(f'Set invalid action type in annex_selected_action. [File Path] : {conflict_annex_path}')
        # git annex lock
        git.git_annex_lock(path=path.HOME_PATH)
        # git commit
        git.git_commmit(msg=message.get('conflict_helper', 'commit_adjust_annex'))
        md.creat_html_msg_info_p(message.get('conflict_helper','complete_adjust_annex'))

        return path_after_rename_list, delete_file_path_list
    else:
        msg = message.get('conflict_helper', 'no_need_adjust_task_notebook')
        md.display_info(msg)
        return [], []

def prepare_sync(path_after_rename_list:list[str], delete_file_path_list:list[str]):
    """4-2. 同期の準備
    """
    try:
        rf_data = get_rf_data()
    except Exception as e:
        err_msg = message.get('DEFAULT', 'unexpected')
        md.display_err(err_msg)
        raise DGTaskError() from e

    # 同期：git pathの作成
    git_sync_paths = list()
    git_confilict_paths = rf_data[KEY_CONFLICT_FILES][KEY_GIT][KEY_GIT_ALL]
    # 競合Gitファイルパスリストの追加
    for git_path in git_confilict_paths:
        git_sync_paths.append(os.path.join(path.HOME_PATH, git_path))
    # 削除ファイルの追加
    for git_path in delete_file_path_list:
        git_sync_paths.append(os.path.join(path.HOME_PATH, git_path))
    # 当該タスクNotebookの追加
    git_sync_paths.append(os.path.join(path.COMMON_DIR_PATH, path.CONFLICT_HELPER))

    # 同期：annex pathの作成
    annex_sync_list = list()
    # リネームリストの追加
    for annex_path in path_after_rename_list:
        annex_sync_list.append(os.path.join(path.HOME_PATH, annex_path))

    commit_msg = message.get('conflict_helper', 'commit_message')

    # gitからの出力結果のエンコードを有効化する
    git.enable_encoding_git()

    # ~/.tmp/rf_form_data/conflict_helper.jsonを削除する。
    common.delete_file(RF_FORM_FILE, raise_err=True)
    md.display_info(message.get('conflict_helper','complete_prepare_sync'))

    return git_sync_paths, annex_sync_list, commit_msg


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

def del_tmp_task_notebooks():
    shutil.rmtree(path.TMP_CONFLICT_DIR)


def save_task_notebooks_to_tmp(filepaths : list):
    for path in filepaths:
        copy_local_content_to_tmp(path)

def save_task_notebooks_to_repo_from_tmp(filepaths : list):
    for path in filepaths:
        copy_tmp_content_to_repo(path)

def copy_tmp_content_to_repo(target_path:str):
    src_path = os.path.join(path.TMP_CONFLICT_DIR, target_path)
    dect_path = os.path.join(path.HOME_PATH, target_path)
    shutil.copy2(src_path, dect_path)


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
                variant_list = annex_rslv_info.get(conflict_annex_path)
                if variant_list is None:
                    variant_list = dict[str, str]()
                abs_candidate_file_path = os.path.join(path.HOME_PATH, candidate_file_path)
                if os.path.isfile(abs_candidate_file_path):
                    variant_list[KEY_LOCAL] =  candidate_file_path
                else:
                    variant_list[KEY_REMOTE] =  candidate_file_path
                annex_rslv_info[conflict_annex_path] = variant_list
    return annex_rslv_info

def dl_data_remote_variatns(annex_rslv_info:dict):
    to_datalad_get_paths = []
    for v in annex_rslv_info.values():
        to_datalad_get_paths.append(
            os.path.join(path.HOME_PATH,v[KEY_REMOTE])
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
KEY_LOCAL_NAME = 'local_name'
KEY_REMOTE_NAME = 'remote_name'
KEY_LOCAL = 'local'
KEY_REMOTE = 'remote'
KEY_FIXATION = 'fixation'

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

def record_rf_data_annex_rename(value:dict, rf_data=None,):
    if rf_data == None:
        rf_data = get_rf_data()

    for path, input in value.items():
        rf_data[KEY_ANNEX_SELECTED_ACTION][path][KEY_LOCAL_NAME] = input[KEY_LOCAL]
        rf_data[KEY_ANNEX_SELECTED_ACTION][path][KEY_REMOTE_NAME] = input[KEY_REMOTE]

    common.create_json_file(RF_DATA_FILE_PATH, rf_data)

def record_rf_data_fixation(rf_data=None,):
    if rf_data == None:
        rf_data = get_rf_data()
    rf_data[KEY_FIXATION] = True
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


def check_key_rf_data(rf_data: dict, need_keys, no_need_keys :list):
    keys = rf_data.keys()

    for need_key in need_keys:
        if need_key not in keys:
            raise NotFoundKey('Required key is included in the data. KEY[{}]'.format(need_key))

    for no_need_key in no_need_keys:
        if no_need_key in keys:
            raise FoundUnnecessarykey('Unnecessary key is included in the data. KEY[{}]'.format(no_need_key))


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

        title = f'{index} : {self.file_path}'
        link = f'../../../../edit/{self.file_path}'
        link_html = pd.create_link(url=link, title=title)
        self.label = pn.pane.HTML(link_html,width=700)

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
                git_conflict_rslv_form_whole_msg.height = 40
                # update conflict_helper.json
                record_rf_data_resolving_git()

        except Exception as e:
            err_msg = message.get('DEFAULT','err_format').format(traceback.format_exc())
            git_conflict_rslv_form_whole_msg.object = md.creat_html_msg_err_p(msg=err_msg)
            git_conflict_rslv_form_whole_msg.height = 60
            self.confirm_button.button_type = 'danger'
            self.confirm_button.name = message.get('DEFAULT', 'unexpected')


def git_conflict_resolve_form(file_paths):
    pn.extension()
    form_items = []
    for index, file_path in enumerate(common.sortFilePath(file_paths)):
        pair = GitFileResolveForm(index, file_path, file_paths)
        form_items.append(pn.Column(pair.label,pair.confirm_button))
    git_conflict_rslv_form_whole_msg.object = ''
    git_conflict_rslv_form_whole_msg.width =700
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

DEFUALT = 'default'
LOCAL_REMAIN = 'local'
REMOTE_REMAIN = 'remote'
BOTH_REMAIN = 'both'

class AnnexFileActionForm:
    """3-2. Annexコンテンツの競合解消アクションフォームクラス
    """
    def __init__(self, rf_data:dict):
        # set rf_data
        self.rf_data = rf_data
        # set confirm_button
        self.confirm_button = pn.widgets.Button(name=message.get('conflict_helper', 'action_confirmed'), button_type='default', width=300)
        self.confirm_button.on_click(self.submit)
        # get file list
        annex_rslv_info = get_annex_rslv_info_from_rf_data(self.rf_data)
        filepaths = common.sortFilePath(list(annex_rslv_info.keys()))

        # generate option on selector
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

            local_path = local_remote[KEY_LOCAL]
            local_link_html = create_edit_link_for_local(local_path)
            local_link = pn.pane.HTML(local_link_html)

            remote_path = local_remote[KEY_REMOTE]
            remoto_link_html = create_edit_link_for_remote(remote_path)
            remoto_link = pn.pane.HTML(remoto_link_html)
            head_data = [base_file, local_link, remoto_link]

            selector = pn.widgets.Select(options=self.options, width=200)
            file_col_data = [head_data, selector]
            self.top_col_data.append(file_col_data)

        self.whole_msg = pn.pane.HTML()
        self.whole_msg.object = ''
        self.whole_msg.width = 700


    def submit(self, event):
        try:
            top_col = self.top_col_data

            annex_selected_action = dict()

            for index in range(self.file_col_num):
                file_col = top_col[index]
                selected_value = file_col[1].value

                if selected_value == DEFUALT:
                    # DEFUALT値が選ばれたら選択エラー、再度入力
                    self.confirm_button.button_type = 'danger'
                    self.confirm_button.name = message.get('conflict_helper', 'select_default_error')
                    return

                base_file_path = file_col[0][0].value
                annex_selected_action[base_file_path] = {'action' : selected_value}

            # update conflict_helper.json
            record_rf_data_annex_selected_action(value=annex_selected_action, rf_data=self.rf_data)
            self.confirm_button.button_type = 'success'
            self.confirm_button.name = message.get('conflict_helper', 'complete_action')
            return
        except Exception:
            err_msg = message.get('DEFAULT','err_format').format(traceback.format_exc())
            self.whole_msg.object = md.creat_html_msg_err_p(msg=err_msg)
            self.whole_msg.height = 60
            self.confirm_button.button_type = 'danger'
            self.confirm_button.name = message.get('DEFAULT', 'unexpected')


def annex_conflict_resolve_action_form(rf_data:dict):
    pn.extension()
    form = AnnexFileActionForm(rf_data)
    top_col = pn.Column()
    for file_col_data in form.top_col_data:
        head_data = file_col_data[0]
        selector = file_col_data[1]
        file_col = pn.Column(*head_data, selector)
        top_col.append(file_col)


    display(pn.Column(top_col, form.confirm_button ,form.whole_msg))


"""
Annexリネーム選択フォーム
"""

class AnnexFileRenameForm:
    """3-3. Annexコンテンツの競合解消リネームフォームクラス
    """
    def __init__(self, rf_data:dict, both_rename_list:list):
        # set rf_data
        self.rf_data = rf_data
        # sort
        both_rename_list = common.sortFilePath(both_rename_list)
        # set both_rename_list
        self.both_rename_list = both_rename_list
        # set button
        self.confirm_button = pn.widgets.Button(name=message.get('conflict_helper', 'rename_confirmed'), button_type='default', width=300)
        self.confirm_button.on_click(self.submit_file_name)

        self.file_col_num = len(both_rename_list)

        self.top_col_data = list()
        for index, both_rename_path in enumerate(both_rename_list):
            varitant_info = rf_data[KEY_ANNEX_CONFLICT_PREPARE_INFO][both_rename_path]
            # create head data
            local_path = varitant_info[KEY_LOCAL]
            local_link_html = create_edit_link_for_local(local_path)
            local_link = pn.pane.HTML(local_link_html)
            remote_path = varitant_info[KEY_REMOTE]
            remoto_link_html = create_edit_link_for_remote(remote_path)
            remoto_link = pn.pane.HTML(remoto_link_html)
            base_file = pn.widgets.StaticText(name=str(index), value=both_rename_path)
            head_data = [base_file, local_link, remoto_link]

            # create local input
            local_input = pn.widgets.TextInput(name=message.get('conflict_helper','local_variant'), placeholder=message.get('conflict_helper','enter_file_name'), width=700)
            # create remote input
            remote_input = pn.widgets.TextInput(name=message.get('conflict_helper','remote_variant'), placeholder=message.get('conflict_helper','enter_file_name'), width=700)
            file_col_data = [head_data, local_input, remote_input]
            self.top_col_data.append(file_col_data)

            self.whole_msg = pn.pane.HTML()
            self.whole_msg.object = ''
            self.whole_msg.width = 700

    def submit_file_name(self, event):
        try:
            submited_top_col_data = self.top_col_data

            input_data = dict()
            for index in range(self.file_col_num):
                # get base file path
                base_file_path = submited_top_col_data[index][0][0].value
                # get input value of local rename
                local_input = submited_top_col_data[index][1].value_input
                # get input value of remote rename
                remote_input = submited_top_col_data[index][2].value_input
                # add form data to input_data
                input_data[base_file_path] = {KEY_LOCAL: local_input, KEY_REMOTE : remote_input}

            err_html = self.validate(input_data)
            if len(err_html) > 0:
                # form err
                self.confirm_button.button_type = 'danger'
                self.confirm_button.name = message.get('conflict_helper', 'invaid_file_name')
                head_err_msg = message.get('conflict_helper','err_head_rename')
                vaild_msg = head_err_msg + err_html
                self.whole_msg.object = md.creat_html_msg_err_p(msg=vaild_msg)
                br_num = vaild_msg.count('<br>') -1
                self.whole_msg.height = 15 * (br_num + 3)
                return
            else:
                # validation OK
                ## 入力情報を記録する
                record_rf_data_annex_rename(value=input_data, rf_data=self.rf_data)
                self.whole_msg.object = ''
                self.whole_msg.height = 5
                self.confirm_button.button_type = 'success'
                self.confirm_button.name = message.get('conflict_helper', 'complete_rename')
                return
        except Exception:
            err_msg=message.get('DEFAULT','err_format').format(traceback.format_exc())
            self.whole_msg.object = md.creat_html_msg_err_p(msg=err_msg)
            self.whole_msg.height = 100
            self.confirm_button.button_type = 'danger'
            self.confirm_button.name = message.get('DEFAULT', 'unexpected')


    def validate(self, input_data:dict)->str:
        ERR_VARIANT_NEME = 'err_variant_name'
        ERR_EMPTY = 'err_empty'
        ERR_EXTENTION = 'err_extention'
        ERR_ALREADY = 'err_already'
        ERR_SLASH = 'err_slash'
        ERR_BACK_SLASH = 'err_back_slash'
        ERR_UNIQUE = 'err_unique'
        ERR_ONE_SIDE_SELECT = 'err_one_side_select'

        # prepare validation
        variant_names = list[str]()
        both_rename_list = self.both_rename_list
        for both_rename_path in both_rename_list:
            varitant_info = self.rf_data[KEY_ANNEX_CONFLICT_PREPARE_INFO][both_rename_path]
            variant_names.append(os.path.basename(varitant_info[KEY_LOCAL]))
            variant_names.append(os.path.basename(varitant_info[KEY_REMOTE]))

        all_conflict_annex_path = list[str]()
        for key in self.rf_data[KEY_ANNEX_SELECTED_ACTION].keys():
            all_conflict_annex_path.append(key)

        not_both_rename_list = list()
        for conflict_annex_path in all_conflict_annex_path:
            if conflict_annex_path not in both_rename_list:
                not_both_rename_list.append(conflict_annex_path)

        input_path = list()
        err_sumary = dict[str, dict[str,list[str]]]()
        for base_file_path, input in input_data.items():
            if err_sumary.get(base_file_path) is None:
                err_sumary[base_file_path] = {KEY_LOCAL:[], KEY_REMOTE:[]}
            local_name = input[KEY_LOCAL]
            remote_name = input[KEY_REMOTE]

            base_dir = os.path.dirname(base_file_path)
            local_path = os.path.join(base_dir, local_name)
            input_path.append(local_path)
            remote_path = os.path.join(base_dir, remote_name)
            input_path.append(remote_path)

            # Localバリデーション
            if len(local_name) <= 0:
                # 空文字だとエラー
                err_sumary[base_file_path][KEY_LOCAL].append(ERR_EMPTY)
            elif '/' in local_name:
                # スラッシュが含まれるとエラー
                err_sumary[base_file_path][KEY_LOCAL].append(ERR_SLASH)
            elif '\\' in local_name:
                 # バックスラッシュが含まれるとエラー
                err_sumary[base_file_path][KEY_LOCAL].append(ERR_BACK_SLASH)
            elif get_extension_for_varinat(base_file_path) != get_extension_for_varinat(local_name):
                # 拡張子が不一致だとエラー
                err_sumary[base_file_path][KEY_LOCAL].append(ERR_EXTENTION)
            elif '.variant-' in local_name:
                # バリアント名だとエラー
                err_sumary[base_file_path][KEY_LOCAL].append(ERR_VARIANT_NEME)
            elif os.path.exists(os.path.join(path.HOME_PATH, local_path)):
                 # 既存ファイルと同名だとエラー
                err_sumary[base_file_path][KEY_LOCAL].append(ERR_ALREADY)
            elif local_path in not_both_rename_list:
                # どちらかを残す選択データと一致していたらエラー
                err_sumary[base_file_path][KEY_LOCAL].append(ERR_ONE_SIDE_SELECT)

            # Remoteバリデーション
            if len(remote_name) <= 0:
                err_sumary[base_file_path][KEY_REMOTE].append(ERR_EMPTY)
            elif '/' in remote_name:
                # スラッシュが含まれるとエラー
                err_sumary[base_file_path][KEY_REMOTE].append(ERR_SLASH)
            elif '\\' in remote_name:
                # バックスラッシュが含まれるとエラー
                err_sumary[base_file_path][KEY_REMOTE].append(ERR_BACK_SLASH)
            elif get_extension_for_varinat(base_file_path) != get_extension_for_varinat(remote_name):
                # 拡張子が不一致だとエラー
                err_sumary[base_file_path][KEY_REMOTE].append(ERR_EXTENTION)
            elif '.variant-' in remote_name:
                # バリアント名だとエラー
                err_sumary[base_file_path][KEY_REMOTE].append(ERR_VARIANT_NEME)
            elif os.path.exists(os.path.join(path.HOME_PATH, remote_path)):
                 # 既存ファイルと同名だとエラー
                err_sumary[base_file_path][KEY_REMOTE].append(ERR_ALREADY)
            elif remote_path in not_both_rename_list:
                # どちらかを残す選択データと一致していたらエラー
                err_sumary[base_file_path][KEY_REMOTE].append(ERR_ONE_SIDE_SELECT)



        # 入力内で重複しているパスを取得する。
        duplicates_paths = list(set([x for x in input_path if input_path.count(x) > 1]))
        ## 重複しているデータを検出して、エラータイプを追加する
        for base_file_path, input in input_data.items():
            base_dir = os.path.dirname(base_file_path)
            local_path = os.path.join(base_dir, input[KEY_LOCAL])
            remote_path = os.path.join(base_dir, input[KEY_REMOTE])

            for duplicates_path in duplicates_paths:
                if local_path == duplicates_path:
                    if not self.has_err_local(err_sumary, base_file_path):
                        err_sumary[base_file_path][KEY_LOCAL].append(ERR_UNIQUE)
                if remote_path == duplicates_path:
                    if not self.has_err_remote(err_sumary, base_file_path):
                        err_sumary[base_file_path][KEY_REMOTE].append(ERR_UNIQUE)

        # err_sumaryとduplicates_pathsに値がある場合、エラー文を作成する。
        new_line = '<br>'
        indent_2 = '<span style="margin-left: 2rem;">'
        indent_4 = '<span style="margin-left: 4rem;">'
        err_msg = ''
        for err_base_path, err_info in err_sumary.items():
            err_local_list = err_info[KEY_LOCAL]
            err_remote_list = err_info[KEY_REMOTE]
            if len(err_local_list)>0 or len(err_remote_list)>0:
                # 不正値があるパスを追加する
                err_msg = err_msg + new_line + err_base_path

                if len(err_local_list)>0:
                    err_msg = err_msg + new_line + indent_2 + message.get('conflict_helper', 'local_variant')
                    for err_type in err_local_list:
                        err_msg = err_msg + new_line + indent_4 + message.get('conflict_helper', err_type)

                if len(err_remote_list)>0:
                    err_msg = err_msg + new_line + indent_2 + message.get('conflict_helper', 'remote_variant')
                    for err_type in err_remote_list:
                        err_msg = err_msg + new_line + indent_4 + message.get('conflict_helper', err_type)
        if len(err_msg) > 0:
            return new_line + err_msg
        else:
            return ''

    def has_err_local(self, err_sumary:dict[str, dict[str,list[str]]], target_path):
        local_errs = err_sumary[target_path][KEY_LOCAL]
        return len(local_errs) > 0

    def has_err_remote(self, err_sumary:dict[str, dict[str,list[str]]], target_path):
        local_errs = err_sumary[target_path][KEY_REMOTE]
        return len(local_errs) > 0



def annex_conflict_resolve_rename_form(rf_data:dict, both_rename_list:list):
    pn.extension()
    form = AnnexFileRenameForm(rf_data, both_rename_list)
    top_col = pn.Column()
    for file_col_data in form.top_col_data:
        head_data = file_col_data[0]
        local_input = file_col_data[1]
        remote_input = file_col_data[2]
        file_col = pn.Column(*head_data, local_input, remote_input)
        top_col.append(file_col)

    display(pn.Column(top_col, form.confirm_button, form.whole_msg))



def create_edit_link_for_local(path:str)->str:
    return create_edit_link(path, message.get('conflict_helper','local_variant'))

def create_edit_link_for_remote(path:str)->str:
    return create_edit_link(path, message.get('conflict_helper','remote_variant'))

def create_edit_link(path:str, title:str)->str:
    url = f'../../../../edit/{path}'
    local_link_html = pd.create_link(url=url, title=title)
    return local_link_html

def not_exec_pre_cell_raise():
    raise_error.not_exec_pre_cell_raise()


def rename_file(base_filepath, future_name)->str:
    dirname = os.path.dirname(base_filepath)
    future_name_filepath = os.path.join(dirname, future_name)
    git.git_mv(base_filepath, future_name_filepath)
    return future_name_filepath
