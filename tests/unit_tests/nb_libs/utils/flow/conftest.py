import os
import pytest

from tests.unit_tests.common.utils import FileUtil
from nb_libs.utils.path.path import SYS_PATH


@pytest.fixture()
def prepare_svg():
    file_res_svg = FileUtil(os.path.join(SYS_PATH, 'research_notebooks.svg'))
    file_res_diag = FileUtil(os.path.join(SYS_PATH, 'research_notebooks.diag'))
    file_exp_svg = FileUtil(os.path.join(SYS_PATH, 'experiment_notebooks.svg'))
    file_exp_diag = FileUtil(os.path.join(SYS_PATH, 'experiment_notebooks.diag'))

    # ファイル削除
    file_res_svg.delete()
    file_res_diag.delete()
    file_exp_svg.delete()
    file_exp_diag.delete()

    yield

    # ファイル削除
    file_res_svg.delete()
    file_res_diag.delete()
    file_exp_svg.delete()
    file_exp_diag.delete()
