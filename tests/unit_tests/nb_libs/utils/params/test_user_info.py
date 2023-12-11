import json
import os

from nb_libs.utils.params.user_info import FILE_PATH, get_user_id, set_user_info


def test_get_user_id(create_user_info_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_user_info.py::test_get_user_id

    user_id = get_user_id()
    assert user_id == 'test_user_id'


def test_set_user_info(delete_user_info_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_user_info.py::test_set_user_info

    set_user_info('test_user_id')
    assert os.path.isfile(FILE_PATH)
    with open(FILE_PATH, 'r') as f:
        data = json.load(f)
    assert data['user_id'] == 'test_user_id'
