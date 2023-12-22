import os
import pytest

from nb_libs.utils.flow.module import (
    orig_diag_file_path,
    diag_file_path,
    svg_file_path,
    display_flow,
    put_mark,
    put_mark_research,
    put_mark_experiment,
    check_finished_setup,
    check_finished_setup_research,
)
from nb_libs.utils.path.path import SYS_PATH, DATA_PATH

from tests.unit_tests.common.utils import FileUtil


def test_orig_diag_file_path():
    # pytest -v -s tests/unit_tests/nb_libs/utils/flow/test_module.py::test_orig_diag_file_path

    path = orig_diag_file_path('research')
    assert path == os.path.join(DATA_PATH, 'flow', 'research_notebooks.diag')


def test_diag_file_path():
    # pytest -v -s tests/unit_tests/nb_libs/utils/flow/test_module.py::test_diag_file_path

    path = diag_file_path('research')
    assert path == os.path.join(SYS_PATH, 'research_notebooks.diag')


def test_svg_file_path():
    # pytest -v -s tests/unit_tests/nb_libs/utils/flow/test_module.py::test_svg_file_path

    path = svg_file_path('research')
    assert path == os.path.join(SYS_PATH, 'research_notebooks.svg')


def test_display_flow(prepare_svg):
    # pytest -v -s tests/unit_tests/nb_libs/utils/flow/test_module.py::test_display_flow

    display_flow('research')
    file_svg = FileUtil(os.path.join(SYS_PATH, 'research_notebooks.svg'))
    assert file_svg.exists()

    display_flow('experiment')
    file_svg = FileUtil(os.path.join(SYS_PATH, 'experiment_notebooks.svg'))
    assert file_svg.exists()

    with pytest.raises(ValueError):
        display_flow('dummy')


def test_put_mark(prepare_svg):
    # pytest -v -s tests/unit_tests/nb_libs/utils/flow/test_module.py::test_put_mark

    put_mark('research', 'base_required_every_time', '済')
    mark_str = '"base_required_every_time"[numbered = 済, fontsize = 10];'
    file_diag = FileUtil(os.path.join(SYS_PATH, 'research_notebooks.diag'))
    with open(file_diag.path, 'r') as f:
        file_contents = f.read()
    assert mark_str in file_contents

    put_mark('experiment', 'required_every_time', '済')
    mark_str = '"required_every_time"[numbered = 済, fontsize = 10];'
    file_diag = FileUtil(os.path.join(SYS_PATH, 'experiment_notebooks.diag'))
    with open(file_diag.path, 'r') as f:
        file_contents = f.read()
    assert mark_str in file_contents


def test_put_mark_research(prepare_svg):
    # pytest -v -s tests/unit_tests/nb_libs/utils/flow/test_module.py::test_put_mark_research

    # エラーが発生しなければOK(test_put_markでパターン網羅済み)
    put_mark_research()


def test_put_mark_experiment(prepare_svg):
    # pytest -v -s tests/unit_tests/nb_libs/utils/flow/test_module.py::test_put_mark_experiment

    # エラーが発生しなければOK(test_put_markでパターン網羅済み)
    put_mark_experiment()


def test_check_finished_setup(prepare_svg):
    # pytest -v -s tests/unit_tests/nb_libs/utils/flow/test_module.py::test_check_finished_setup

    # ファイルが存在しない
    assert not check_finished_setup('research', 'base_required_every_time', '済')

    file_diag_org = FileUtil(os.path.join(DATA_PATH, 'flow', 'research_notebooks.diag'))
    file_diag = file_diag_org.copy(os.path.join(SYS_PATH, 'research_notebooks.diag'))

    # セットアップ未完了
    assert not check_finished_setup('research', 'base_required_every_time', '済')

    data = file_diag.read()
    before = '"base_required_every_time"[fontsize = 10];'
    after = '"base_required_every_time"[numbered = 済, fontsize = 10];'
    data = data.replace(before, after)
    file_diag.create(data)

    # セットアップ完了済み
    assert check_finished_setup('research', 'base_required_every_time', '済')


def test_check_finished_setup_research(prepare_svg):
    # pytest -v -s tests/unit_tests/nb_libs/utils/flow/test_module.py::check_finished_setup_research

    # エラーが発生しなければOK(test_check_finished_setupでパターン網羅済み)
    check_finished_setup_research()
