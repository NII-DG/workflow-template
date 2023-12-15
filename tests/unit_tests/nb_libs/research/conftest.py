
import pytest

from nb_libs.utils.params import token, user_info

from tests.unit_tests.common.utils import FileUtil

file_user = FileUtil(user_info.FILE_PATH)
file_token = FileUtil(token.FILE_PATH)


@pytest.fixture()
def prepare_preparation_completed():
    # ファイル削除
    file_user.delete()
    file_token.delete()

    yield

    # ファイル削除
    file_user.delete()
    file_token.delete()
