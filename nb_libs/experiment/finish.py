import os

from ..utils.ex_utils import package as ex_pkg
from ..utils.message import message as msg_mod
from ..utils.params import ex_pkg_info
from ..utils.path import path as p


def syncs_config() -> tuple[list[str], list[str], list[str], str]:
    """同期のためにファイルとメッセージの設定"""
    # get experiment title
    experiment_title = ex_pkg_info.exec_get_ex_title()
    # set sync path
    git_path, gitannex_path, gitannex_files = ex_pkg.create_syncs_path(p.create_experiments_with_subpath(experiment_title))
    nb_path = os.path.join(p.EXP_DIR_PATH, 'finish.ipynb')
    git_path.append(nb_path)
    # set commit message
    commit_message = msg_mod.get('commit_message', 'finish_ex').format(experiment_title)
    return git_path, gitannex_path, gitannex_files, commit_message
