import os

from nb_libs.utils.ex_utils.package import (
    create_ex_package,
    create_param_folder,
    create_syncs_path,
)
from nb_libs.utils.path.path import EXPERIMENTS_PATH, DATA_PATH

from tests.unit_tests.common.utils import FileUtil, DirUtil


def test_create_ex_package(prepare_package):
    # pytest -v -s tests/unit_tests/nb_libs/utils/ex_utils/test_package.py::test_create_ex_package

    exp_dir = DirUtil(prepare_package)

    create_ex_package('with_code', exp_dir.path)
    base_dir = DirUtil(os.path.join(DATA_PATH, 'PACKAGE', 'base'))
    scheme_dir = DirUtil(os.path.join(DATA_PATH, 'PACKAGE', 'scheme', 'with_code'))
    expected = sorted(base_dir.children() + scheme_dir.children())
    assert sorted(exp_dir.children()) == expected


def test_create_param_folder(prepare_package):
    # pytest -v -s tests/unit_tests/nb_libs/utils/ex_utils/test_package.py::test_create_param_folder

    exp_dir = DirUtil(prepare_package)

    create_param_folder(exp_dir.path)
    param_dir = DirUtil(os.path.join(DATA_PATH, 'PACKAGE', 'scheme', 'for_parameters', 'parameter'))
    expected = sorted(param_dir.children())
    assert sorted(exp_dir.children()) == expected


def test_create_syncs_path(prepare_package):
    # pytest -v -s tests/unit_tests/nb_libs/utils/ex_utils/test_package.py::test_create_syncs_path

    exp_dir = DirUtil(prepare_package)
    exp_dir.delete()
    exp_dir.create()

    # with_code
    file1 = FileUtil(os.path.join(exp_dir.path, 'file.txt'))
    file1.create()
    dir_input = DirUtil(os.path.join(exp_dir.path, 'input_data'))
    dir_input.create()
    file2 = FileUtil(os.path.join(dir_input.path, 'file.txt'))
    file2.create()
    dir_output2 = DirUtil(os.path.join(dir_input.path, 'output_data'))
    dir_output2.create()
    file3 = FileUtil(os.path.join(dir_output2.path, 'file.txt'))
    file3.create()
    dir_output = DirUtil(os.path.join(exp_dir.path, 'output_data'))
    dir_output.create()
    file4 = FileUtil(os.path.join(dir_output.path, 'file.txt'))
    file4.create()
    dir_ci = DirUtil(os.path.join(exp_dir.path, 'ci'))
    dir_ci.create()
    file5 = FileUtil(os.path.join(dir_ci.path, 'file.txt'))
    file5.create()
    dir_source = DirUtil(os.path.join(exp_dir.path, 'source'))
    dir_source.create()
    file6 = FileUtil(os.path.join(dir_source.path, 'file.txt'))
    file6.create()
    dir_test = DirUtil(os.path.join(dir_source.path, 'test'))
    dir_test.create()
    file7 = FileUtil(os.path.join(dir_test.path, 'file.txt'))
    file7.create()

    git_path, gitannex_path, gitannex_files = create_syncs_path(exp_dir.path)
    assert sorted(git_path) == sorted([file1.path, dir_ci.path, dir_source.path])
    assert sorted(gitannex_path) == sorted([dir_input.path, dir_output.path])
    assert sorted(gitannex_files) == sorted([file2.path, file3.path, file4.path])

    exp_dir.delete()
    exp_dir.create()

    # for_parameters
    file1 = FileUtil(os.path.join(exp_dir.path, 'file.txt'))
    file1.create()
    dir_input = DirUtil(os.path.join(exp_dir.path, 'input_data'))
    dir_input.create()
    file2 = FileUtil(os.path.join(dir_input.path, 'file.txt'))
    file2.create()
    dir_output2 = DirUtil(os.path.join(dir_input.path, 'output_data'))
    dir_output2.create()
    file3 = FileUtil(os.path.join(dir_output2.path, 'file.txt'))
    file3.create()
    dir_ci = DirUtil(os.path.join(exp_dir.path, 'ci'))
    dir_ci.create()
    file4 = FileUtil(os.path.join(dir_ci.path, 'file.txt'))
    file4.create()
    dir_source = DirUtil(os.path.join(exp_dir.path, 'source'))
    dir_source.create()
    file5 = FileUtil(os.path.join(dir_source.path, 'file.txt'))
    file5.create()
    dir_test = DirUtil(os.path.join(dir_source.path, 'test'))
    dir_test.create()
    file6 = FileUtil(os.path.join(dir_test.path, 'file.txt'))
    file6.create()
    dir_param = DirUtil(os.path.join(exp_dir.path, 'param1'))
    dir_param.create()
    dir_params = DirUtil(os.path.join(dir_param.path, 'params'))
    dir_params.create()
    file7 = FileUtil(os.path.join(dir_params.path, 'file.txt'))
    file7.create()
    dir_output = DirUtil(os.path.join(dir_param.path, 'output_data'))
    dir_output.create()
    file8 = FileUtil(os.path.join(dir_output.path, 'file.txt'))
    file8.create()

    git_path, gitannex_path, gitannex_files = create_syncs_path(exp_dir.path)
    assert sorted(git_path) == sorted([file1.path, dir_ci.path, dir_source.path, dir_params.path])
    assert sorted(gitannex_path) == sorted([dir_input.path, dir_output.path])
    assert sorted(gitannex_files) == sorted([file2.path, file3.path, file8.path])
