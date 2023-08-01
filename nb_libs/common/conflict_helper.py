import os
from ..utils.params import ex_pkg_info as epi
from ..utils.path import path, display as pd
from ..utils.message import message, display as md
from ..utils.git import git_module as git
from ..utils.except_class import DGTaskError
from IPython.display import HTML, display



def analyze_conflict_status():
    """1. 競合状態の解析
    """
    # check exist conflict_helper.json
    if exist_rf_form_file():
        ## No processing is performed because this task is running
        err_msg = message.get('task', 'in_progress')
        md.display_warm(err_msg)
        return
    else:
        # Start analyzing the state of contention
        ## Disable git output encoding
        git.disable_encoding_git()




    pass

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
