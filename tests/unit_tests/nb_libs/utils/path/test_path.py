import os

from nb_libs.utils.path.path import HOME_PATH, create_experiments_with_subpath


def test_create_experiments_with_subpath():
    # pytest -v -s tests/nb_libs/utils/path/path.py::test_create_experiments_with_subpath

    # sub_pathなし
    ret = create_experiments_with_subpath('title1')
    expected = os.path.join(HOME_PATH, 'experiments/title1')
    assert ret == expected

    # sub_pathあり
    ret = create_experiments_with_subpath('title1', 'input_data/dir/file1.txt')
    expected = os.path.join(HOME_PATH, 'experiments/title1/input_data/dir/file1.txt')
    assert ret == expected
