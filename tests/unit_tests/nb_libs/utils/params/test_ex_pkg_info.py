import pytest

from nb_libs.utils.params.ex_pkg_info import (
    FILE_PATH,
    get_current_experiment_title,
    exec_get_ex_title,
    set_current_experiment_title,
    exist_file,
)
from nb_libs.utils.except_class import DGTaskError

from tests.unit_tests.common.utils import FileUtil


def test_get_current_experiment_title(prepare_ex_pkg_info_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_ex_pkg_info.py::test_get_current_experiment_title

    ex_pkg_info = FileUtil(FILE_PATH)

    # 正常ケース
    ex_pkg_info.create_json({'ex_pkg_name': 'test_package'})
    title = get_current_experiment_title()
    assert title == 'test_package'

    # 取得失敗のケース
    ex_pkg_info.delete()
    title = get_current_experiment_title()
    assert title == None


def test_exec_get_ex_title(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_ex_pkg_info.py::exec_get_ex_title

    # 正常ケース
    mocker.patch('nb_libs.utils.params.ex_pkg_info.get_current_experiment_title', return_value='test_package')
    title = exec_get_ex_title()
    assert title == 'test_package'

    # 取得失敗のケース
    mocker.patch('nb_libs.utils.params.ex_pkg_info.get_current_experiment_title', return_value=None)
    with pytest.raises(DGTaskError):
        exec_get_ex_title()
        exec_get_ex_title(display_error=False)


def test_set_current_experiment_title(prepare_ex_pkg_info_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_ex_pkg_info.py::test_set_current_experiment_title

    ex_pkg_info = FileUtil(FILE_PATH)
    ex_pkg_info.delete()

    set_current_experiment_title('test_package')
    assert ex_pkg_info.exists()
    data = ex_pkg_info.read_json()
    assert data['ex_pkg_name'] == 'test_package'


def test_exist_file(prepare_ex_pkg_info_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_ex_pkg_info.py::test_exist_file

    ex_pkg_info = FileUtil(FILE_PATH)

    # ファイルが存在するケース
    ex_pkg_info.create_json({'ex_pkg_name': 'test_package'})
    assert exist_file()

    # ファイルが存在しないケース
    ex_pkg_info.delete()
    assert not exist_file()
