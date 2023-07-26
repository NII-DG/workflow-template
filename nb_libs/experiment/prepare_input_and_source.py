from IPython.display import HTML, display

import nb_libs.utils.message.message as message
import nb_libs.utils.path.path as path
from nb_libs.utils.path.display import button_html

MESSAGE_SECTION_NAME = 'prepare_input_and_source'


def create_ref_prepare_from_repository():
    display(HTML(button_html(path.PREPARE_FROM_REPOSITORY, message.get(
        MESSAGE_SECTION_NAME, 'prepare_from_gin_fork_title'))))


def create_ref_prepare_unit_from_s3():
    display(HTML(button_html(path.PREPARE_UNIT_FROM_S3, message.get(
        MESSAGE_SECTION_NAME, 'prepare_unit_from_s3_title'))))


def create_ref_prepare_multi_from_s3():
    display(HTML(button_html(path.PREPARE_MULTI_FROM_S3, message.get(
        MESSAGE_SECTION_NAME, 'prepare_multi_from_s3_title'))))


def create_ref_prepare_from_local():
    display(HTML(button_html(path.PREPARE_FROM_LOCAL, message.get(
        MESSAGE_SECTION_NAME, 'prepare_from_local_title'))))
