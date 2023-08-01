import os
from ..utils.message import message, display as display_util
from ..utils.path import path
from ..utils.params.ex_pkg_info import get_current_experiment_title
from ..utils.gin import sync
from ..utils.path.display import button_html
from IPython.display import display, HTML


MESSAGE_SECTION_NAME = 'describe_experiment'


def create_ref_readme():
    experiment_title = get_current_experiment_title()

    if experiment_title is not None:
        readme_path = os.path.join(
            '..', '..', '..', '..', 'edit', 'experiments', experiment_title, path.README_FILE)
        display(HTML(button_html(readme_path, message.get(
            MESSAGE_SECTION_NAME, 'readme_ref_title'), target='_blank')))
    else:
        display_util.display_err(message.get(
            'experiment_error', 'experiment_setup_unfinished'))


def sync_experiment_description():
    experiment_title = get_current_experiment_title()

    if experiment_title is not None:
        readme_path = path.create_experiments_with_subpath(
            experiment_title, sub_path=path.README_FILE)
        describe_experiment_path = os.path.join(
            path.EXP_DIR_PATH, path.DESCRIBE_EXPERIMENT)
        git_path = [readme_path, describe_experiment_path]
        git_log = experiment_title + \
            message.get(MESSAGE_SECTION_NAME, 'describe_experiment_log_suffix')
        return sync.syncs_with_repo(git_path=git_path, gitannex_path=[], gitannex_files=[], message=git_log, get_paths=[])
    else:
        display_util.display_err(message.get(
            'experiment_error', 'experiment_setup_unfinished'))
        return False
