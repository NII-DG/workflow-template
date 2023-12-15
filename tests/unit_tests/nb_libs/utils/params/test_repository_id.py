from nb_libs.utils.params.repository_id import FILE_PATH, get_repo_id

from tests.unit_tests.common.utils import FileUtil


def test_get_repo_id(prepare_repo_id_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_repository_id.py::test_get_repo_id

    # ファイル作成
    repo_id = FileUtil(FILE_PATH)
    repo_id.create('test_repo_id')

    repo_id = get_repo_id()
    assert repo_id == 'test_repo_id'
