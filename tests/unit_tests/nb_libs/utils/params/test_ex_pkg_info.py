import json
import os
import pytest

from nb_libs.utils.params.ex_pkg_info import (
    FILE_PATH,
    get_current_experiment_title,
    exec_get_ex_title,
    set_current_experiment_title,
    exist_file,
)
from nb_libs.utils.except_class import DGTaskError


def test_get_current_experiment_title(create_ex_pkg_info_file):
    # pytest -v -s tests/nb_libs/utils/params/test_ex_pkg_info.py::test_get_current_experiment_title

    # 正常ケース
    title = get_current_experiment_title()
    assert title == 'test_package'

    # 取得失敗のケース
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)
    title = get_current_experiment_title()
    assert title == None


def test_exec_get_ex_title(mocker):
    # pytest -v -s tests/nb_libs/utils/params/test_ex_pkg_info.py::exec_get_ex_title

    # 正常ケース
    mocker.patch('nb_libs.utils.params.ex_pkg_info.get_current_experiment_title', return_value='test_package')
    title = exec_get_ex_title()
    assert title == 'test_package'

    # 取得失敗のケース
    mocker.patch('nb_libs.utils.params.ex_pkg_info.get_current_experiment_title', return_value=None)
    with pytest.raises(DGTaskError):
        exec_get_ex_title()
        exec_get_ex_title(display_error=False)


def test_set_current_experiment_title(delete_ex_pkg_info_file):
    # pytest -v -s tests/nb_libs/utils/params/test_ex_pkg_info.py::test_set_current_experiment_title

    set_current_experiment_title('test_package')
    assert os.path.isfile(FILE_PATH)
    with open(FILE_PATH, 'r') as f:
        data = json.load(f)
    assert data['ex_pkg_name'] == 'test_package'


def test_exist_file(create_ex_pkg_info_file):
    # pytest -v -s tests/nb_libs/utils/params/test_ex_pkg_info.py::test_exist_file

    # ファイルが存在するケース
    assert exist_file()

    # ファイルが存在しないケース
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)
    assert not exist_file()
