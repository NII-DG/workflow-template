import json
import os
import pytest

from nb_libs.utils.common.common import (
    get_AND_elements,
    decode_exec_subprocess,
    exec_subprocess,
    is_should_annex_content_path,
    has_unicode_escape,
    get_filepaths_from_dalalad_error,
    get_AND_dirpaths,
    get_AND_absolutedirpaths,
    sortFilePath,
    convert_url_remove_user_token,
    delete_file,
    cp_dir,
    cp_file,
    create_json_file,
    read_json_file,
    not_exec_pre_cell,
)

from nb_libs.utils.path.path import HOME_PATH
from nb_libs.utils.except_class import ExecCmdError


def test_get_AND_elements():
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::test_get_AND_elements

    list_a = ['test1', 'test1', 'test2', 'test3']
    list_b = ['test1', 'test3', 'test4', 'test4', 'test5']
    ret = get_AND_elements(list_a, list_b)
    assert len(ret) == 2
    assert 'test1' in ret
    assert 'test3' in ret


def test_decode_exec_subprocess(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::test_decode_exec_subprocess

    stdout = 'test_stdout'.encode('utf-8')
    stderr = 'test_stderr'.encode('utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, stderr, 0))
    ret = decode_exec_subprocess('echo test')
    assert ret[0] == 'test_stdout'
    assert ret[1] == 'test_stderr'
    assert ret[2] == 0


def test_exec_subprocess():
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::test_exec_subprocess

    command_normal = 'echo test'
    command_stderr = 'echo test 1>&2'
    command_error = 'echo test 1>&2 | false'

    # 正常ケース
    stdout, stderr, rt = exec_subprocess(command_normal)
    assert stdout == 'test\n'.encode('utf-8')
    assert stderr == ''.encode('utf-8')
    assert rt == 0

    stdout, stderr, rt = exec_subprocess(command_normal, HOME_PATH)
    assert stdout == 'test\n'.encode('utf-8')
    assert stderr == ''.encode('utf-8')
    assert rt == 0

    # 正常ケース(標準エラー)
    stdout, stderr, rt = exec_subprocess(command_stderr)
    assert stdout == ''.encode('utf-8')
    assert stderr == 'test\n'.encode('utf-8')
    assert rt == 0

    # コマンド実行失敗(raise_error:True)
    with pytest.raises(ExecCmdError) as e:
        stdout, stderr, rt = exec_subprocess(command_error)
    assert str(e.value) == 'command return code is not 0. got 1. stderr = test\n'

    # コマンド実行失敗(raise_error:False)
    stdout, stderr, rt = exec_subprocess(command_error, raise_error=False)
    assert stdout == ''.encode('utf-8')
    assert stderr == 'test\n'.encode('utf-8')
    assert rt == 1


def test_is_should_annex_content_path():
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::is_should_annex_content_path

    assert is_should_annex_content_path('experiments/test_package/input_data/file1.txt')
    assert is_should_annex_content_path('experiments/test_package/output_data/file1.txt')

    assert not is_should_annex_content_path('experiments/test_package/input_data/.gitkeep')
    assert not is_should_annex_content_path('experiments/test_package/output_data/.gitkeep')

    assert not is_should_annex_content_path('experiments/test_package/source/file1.py')
    assert not is_should_annex_content_path('experiments/test_package/ci/file1.py')

    assert is_should_annex_content_path('experiments/test_package/test_param/output_data/file1.txt')
    assert is_should_annex_content_path('experiments/test_package/test_param/output_data/.gitkeep')

    assert not is_should_annex_content_path('experiments/test_package/test_param/input_data/file1.txt')

    assert not is_should_annex_content_path('experiments/file1.py')

    assert not is_should_annex_content_path('dmp.json')


def test_has_unicode_escape():
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::test_has_unicode_escape

    assert has_unicode_escape(r'\u0aA0')
    assert not has_unicode_escape(r'\u0aAG')
    assert not has_unicode_escape(r'\U0aA0')


def test_get_filepaths_from_dalalad_error():
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::test_get_filepaths_from_dalalad_error

    err_info = [
        r"'\t" + "dir1/test1.txt" + r"\n'",
        r"'\t" + "dir2/test2.txt" + r"\n'",
        r"'\t" + "" + r"\n'",               # ファイルパスが空欄
    ]
    ret = get_filepaths_from_dalalad_error(''.join(err_info))
    assert ret == ['dir1/test1.txt', 'dir2/test2.txt']


def test_get_AND_dirpaths():
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::test_get_AND_dirpaths

    paths = [
        'dir1/dir2/file1.txt',
        'dir1/file2.txt',
        'dir1/dir2/file3.txt',
        'dir1/dir2/dir3/file4.txt',
    ]
    ret = get_AND_dirpaths(paths)
    assert ret == ['dir1/dir2', 'dir1', 'dir1/dir2/dir3']


def test_get_AND_absolutedirpaths():
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::test_get_AND_absolutedirpaths

    paths = [
        'dir1/dir2/file1.txt',
        'dir1/file2.txt',
        'dir1/dir2/file3.txt',
        'dir1/dir2/dir3/file4.txt',
    ]
    ret = get_AND_absolutedirpaths(paths)
    # assert ret == [
    #     HOME_PATH + '/dir1/dir2',
    #     HOME_PATH + '/dir1',
    #     HOME_PATH + '/dir1/dir2/dir3'
    # ]
    assert ret == [
        HOME_PATH + '/dir1/dir2',
    ]


def test_sortFilePath():
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::test_sortFilePath

    paths = [
        'dir1/dir2/file10.txt',
        'dir1/dir2/file.txt',
        'dir1/dir2/file1.txt',
        'dir10/file2.txt',
        'dir10/dir2/file3.txt',
        'dir1/dir1/dir3/file4.txt',
        'dir1/dir2/file.jpg',
    ]
    ret = sortFilePath(paths)
    assert ret == [
        'dir1/dir1/dir3/file4.txt',
        'dir1/dir2/file.jpg',
        'dir1/dir2/file.txt',
        'dir1/dir2/file1.txt',
        'dir1/dir2/file10.txt',
        'dir10/dir2/file3.txt',
        'dir10/file2.txt',
    ]


def test_convert_url_remove_user_token():
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::test_convert_url_remove_user_token

    # パブリックリポジトリ
    url = 'https://test.github-domain/test_user/test_repo.git'
    ret = convert_url_remove_user_token(url)
    assert ret == ('https://test.github-domain/test_user/test_repo.git', '')

    # プライベートリポジトリ
    url = 'https://user:token@test.github-domain/test_user/test_repo.git'
    ret = convert_url_remove_user_token(url)
    assert ret == ('https://test.github-domain/test_user/test_repo.git', 'token')


def test_delete_file(create_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::test_delete_file

    # ファイルが存在しない
    path_not_exist = create_file['not_exist']
    delete_file(path_not_exist)
    with pytest.raises(FileNotFoundError) as e:
        delete_file(create_file['not_exist'], raise_err=True)
    assert str(e.value) == f'Not Found File : {path_not_exist}'
    assert not os.path.isfile(path_not_exist)

    # ファイルが存在する
    path_exist = create_file['exist']
    delete_file(path_exist)
    assert not os.path.isfile(path_exist)


def test_cp_dir(prepare_cp_dir):
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::test_cp_dir

    src = prepare_cp_dir['src']
    dst = prepare_cp_dir['dst']
    cp_dir(src, dst)

    # フォルダとファイルがコピーされることを確認
    assert sorted(os.listdir(dst)) == ['dir1', 'dir2', 'dir3', 'file0_1.txt', 'file0_2.txt', 'file0_3.txt']

    # 同じ名前のファイルは上書きされないことを確認
    dst_file01 = os.path.join(dst, 'file0_1.txt')
    with open(dst_file01, mode='r') as f:
        data = f.read()
    assert data == 'dst_file01'
    dst_file11 = os.path.join(dst, 'dir1', 'file1_1.txt')
    with open(dst_file11, mode='r') as f:
        data = f.read()
    assert data == 'dst_file11'

    # コピー先に存在しないファイルはコピーされることを確認
    # dst_file12 = os.path.join(dst, 'dir1', 'file1_2.txt')
    # assert os.path.isfile(dst_file12)
    dst_file21 = os.path.join(dst, 'dir2', 'file2_1.txt')
    assert os.path.isfile(dst_file21)

    # コピー元に存在しないファイルはそのまま存在することを確認
    dst_file13 = os.path.join(dst, 'dir1', 'file1_3.txt')
    assert os.path.isfile(dst_file13)
    dst_file31 = os.path.join(dst, 'dir3', 'file3_1.txt')
    assert os.path.isfile(dst_file31)


def test_cp_file(prepare_cp_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::test_cp_file

    src = prepare_cp_file['src']
    dst = prepare_cp_file['dst']

    # フォルダが存在しないケース
    src_file11 = os.path.join(src, 'dir1', 'file1_1.txt')
    dst_file11 = os.path.join(dst, 'dir1', 'file1_1.txt')
    cp_file(src_file11, dst_file11)
    assert os.path.isfile(dst_file11)

    # ファイルが存在しないケース
    src_file21 = os.path.join(src, 'dir2', 'file2_1.txt')
    dst_file21 = os.path.join(dst, 'dir2', 'file2_1.txt')
    cp_file(src_file21, dst_file21)
    assert os.path.isfile(dst_file21)

    # ファイルが存在するケース(上書き)
    src_file22 = os.path.join(src, 'dir2', 'file2_2.txt')
    dst_file22 = os.path.join(dst, 'dir2', 'file2_2.txt')
    cp_file(src_file22, dst_file22)
    assert os.path.isfile(dst_file22)
    with open(dst_file22, mode='r') as f:
        data = f.read()
    assert data == 'src_file22'


def test_create_json_file(prepare_create_json_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::test_create_json_file

    work_dir = prepare_create_json_file
    test_json = {'test_key': 'test_value'}

    # フォルダが存在しないケース
    file1 = os.path.join(work_dir, 'dir', 'file1.json')
    create_json_file(file1, test_json)
    assert os.path.isfile(file1)

    # ファイルが存在しないケース
    file2 = os.path.join(work_dir, 'file2.json')
    create_json_file(file2, test_json)
    assert os.path.isfile(file2)

    # ファイルが存在するケース(上書き)
    file3 = os.path.join(work_dir, 'exist.json')
    create_json_file(file3, test_json)
    assert os.path.isfile(file3)
    with open(file3, mode='r') as f:
        data = json.load(f)
    assert 'exist_key' not in data
    assert data['test_key'] == 'test_value'


def test_read_json_file(prepare_read_json_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::test_read_json_file

    file = prepare_read_json_file
    data = read_json_file(file)
    assert data['test_key'] == 'test_value'


def test_not_exec_pre_cell():
    # pytest -v -s tests/unit_tests/nb_libs/utils/common/test_common.py::test_not_exec_pre_cell

    # エラーが発生しなければOK
    not_exec_pre_cell()
