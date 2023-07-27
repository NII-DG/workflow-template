import os

from IPython.display import display, HTML

import nb_libs.utils.message.display as display_util
import nb_libs.utils.message.message as message
import nb_libs.utils.path.path as path
from nb_libs.utils.gin import sync
from nb_libs.utils.params.ex_pkg_name import get_current_experiment_title
from nb_libs.utils.path.display import button_html

MESSAGE_SECTION_NAME = 'describe_snakefile'


def create_ref_snakefile():
    experiment_title = get_current_experiment_title()

    if experiment_title is not None:
        snakefile_path = os.path.join(
            '..', '..', '..', '..', 'edit', 'experiments', experiment_title, path.SNAKE_FILE)
        display(HTML(button_html(snakefile_path, message.get(
            MESSAGE_SECTION_NAME, 'snakefile_ref_title'), target='_blank')))
    else:
        display_util.display_err(message.get(
            'experiment_error', 'experiment_setup_unfinished'))


def create_ref_how_to_make_snakefile():
    snakefile_manual_path = os.path.join(
        path.SNAKE_DOC_DIR, path.HOW_TO_SNAKE_MAKE)
    display(HTML(button_html(snakefile_manual_path, message.get(
        MESSAGE_SECTION_NAME, 'how_to_make_snakefile_ref_title'), target='_blank')))


def sync_snakefile_description():
    experiment_title = get_current_experiment_title()

    if experiment_title is not None:
        snakefile_path = path.create_experiments_with_subpath(
            experiment_title, sub_path=path.SNAKE_FILE)
        describe_snakefile_path = os.path.join(
            path.EXP_DIR_PATH, path.DESCRIBE_SNAKEFILE)
        git_path = [snakefile_path, describe_snakefile_path]
        log_suffix = message.get(MESSAGE_SECTION_NAME,
                                 'describe_snakefile_log_suffix')
        return sync.syncs_with_repo(git_path=git_path, gitannex_path=[], gitannex_files=[],
                                    message=experiment_title + log_suffix, get_paths=[])
    else:
        display_util.display_err(message.get(
            'experiment_error', 'experiment_setup_unfinished'))
        return False
