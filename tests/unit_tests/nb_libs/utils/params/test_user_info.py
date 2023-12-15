from nb_libs.utils.params.user_info import FILE_PATH, get_user_id, set_user_info

from tests.unit_tests.common.utils import FileUtil


def test_get_user_id(prepare_user_info_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_user_info.py::test_get_user_id

    # ファイル作成
    user_info = FileUtil(FILE_PATH)
    user_info.create_json({'user_id': 'test_user_id'})

    user_id = get_user_id()
    assert user_id == 'test_user_id'


def test_set_user_info(prepare_user_info_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_user_info.py::test_set_user_info

    # ファイル削除
    user_info = FileUtil(FILE_PATH)
    user_info.delete()

    set_user_info('test_user_id')
    assert user_info.exists()
    data = user_info.read_json()
    assert data['user_id'] == 'test_user_id'
