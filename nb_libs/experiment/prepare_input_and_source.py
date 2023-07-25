import os

from IPython.display import display

import nb_libs.utils.message.message as message
import nb_libs.utils.path.path as path
from nb_libs.utils.path.display import button_html


MESSAGE_SECTION_NAME = 'describe_snakefile'


def create_ref_prepare_from_repository():
    readme_path = os.join(path.EXP_DIR_PATH, path.PREPARE_FROM_REPOSITORY)
    display(button_html(readme_path, message.get(
        MESSAGE_SECTION_NAME, 'prepare_from_gin_fork_title')))


def create_ref_prepare_unit_from_s3():
    readme_path = os.join(path.EXP_DIR_PATH, path.PREPARE_UNIT_FROM_S3)
    display(button_html(readme_path, message.get(
        MESSAGE_SECTION_NAME, 'prepare_unit_from_s3_title')))


def create_ref_prepare_multi_from_s3():
    readme_path = os.join(path.EXP_DIR_PATH, path.PREPARE_MULTI_FROM_S3)
    display(button_html(readme_path, message.get(
        MESSAGE_SECTION_NAME, 'prepare_multi_from_s3_title')))


def create_ref_prepare_from_local():
    readme_path = os.join(path.EXP_DIR_PATH, path.PREPARE_FROM_LOCAL)
    display(button_html(readme_path, message.get(
        MESSAGE_SECTION_NAME, 'prepare_from_local_title')))