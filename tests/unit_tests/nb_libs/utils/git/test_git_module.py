from nb_libs.utils.git.git_module import (
    exec_git_status,
    exec_git_branch,
    exec_git_annex_whereis,
    git_annex_add,
    git_add,
    git_commmit,
    git_mv,
    git_ls_files,
    disable_encoding_git,
    enable_encoding_git,
    git_annex_lock,
    git_annex_unlock,
    git_annex_remove_metadata,
    git_annex_unannex,
    git_annex_resolvemerge,
    git_annex_untrust,
    git_annex_trust,
    git_annex_whereis,
    git_annex_metadata_add_minetype_sha256_contentsize,
    git_annex_metadata_add_sd_date_published,
    get_conflict_filepaths,
    get_modified_filepaths,
    get_delete_filepaths,
    get_annex_content_file_paht_list,
    get_remote_annex_variant_path,
    get_local_object_hash_by_path,
    get_multi_local_object_hash_by_path,
    is_conflict,
    get_remote_url,
    get_current_branch,
)

from nb_libs.utils.path.path import HOME_PATH

git_status_no_change = [
    'On branch develop',
    'Your branch is up to date with \'origin/develop\'.',
    '',
    'nothing to commit, working tree clean',
]
"""変更なしの場合のgit status実行結果"""

git_status_modified = [
    'On branch develop',
    'Your branch is up to date with \'origin/develop\'.',
    '',
    'Changes not staged for commit:',
    '  (use "git add/rm <file>..." to update what will be committed)',
    '  (use "git restore <file>..." to discard changes in working directory)',
    '	deleted:    dir1/delete exist space.py',
    '	deleted:    dir1/delete.py',
    '	modified:   dir1/modified exist space.py',
    '	modified:   dir1/modified.py',
    '',
    'Untracked files:',
    '  (use "git add <file>..." to include in what will be committed)',
    '	dir1/add exist space.py',
    '	dir1/add.py',
    '',
    'no changes added to commit (use "git add" and/or "git commit -a")',
]
"""変更ありの場合のgit status実行結果"""

git_status_staging = [
    'On branch develop',
    'Your branch is up to date with \'origin/develop\'.',
    '',
    'Changes to be committed:',
    '  (use "git restore --staged <file>..." to unstage)',
    '	new file:   dir1/add exist space.py',
    '	new file:   dir1/add.py',
    '	new file:   dir1/add exist space.variant-.py',
    '	new file:   dir1/add.variant-.py',
    '	deleted:    dir1/delete exist space.py',
    '	deleted:    dir1/delete.py',
    '	modified:   dir1/modified exist space.py',
    '	modified:   dir1/modified.py',
]
"""ステージング済みの場合のgit status実行結果"""

git_status_conflict = [
    'On branch develop',
    'Your branch and \'origin/develop\' have diverged,'
    'and have 2 and 2 different commits each, respectively.',
    '  (use "git pull" to merge the remote branch into yours)',
    '',
    'You have unmerged paths.',
    '  (fix conflicts and run "git commit")',
    '  (use "git merge --abort" to abort the merge)',
    '',
    'Changes to be committed:',
    '	new file:   dir1/add1 exist space.variant-.py',
    '	new file:   dir1/add1.variant-.py',
    '	new file:   dir1/add1 exist space.py',
    '	new file:   dir1/add1.py',
    '	deleted:    dir1/delete1 exist space.py',
    '	deleted:    dir1/delete1.py',
    '	modified:   dir1/modified1 exist space.py',
    '	modified:   dir1/modified1.py',
    '',
    'Unmerged paths:',
    '  (use "git add <file>..." to mark resolution)',
    '	both added:      dir1/add2 exist space.py',
    '	both added:      dir1/add2.py',
    '	both modified:   dir1/modified2 exist space.py',
    '	both modified:   dir1/modified2.py',
    '',
    'no changes added to commit (use "git add" and/or "git commit -a")',
]
"""競合ありの場合のgit status実行結果"""


def test_exec_git_status(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_exec_git_status

    stdout = 'test output'.encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = exec_git_status()
    assert ret == 'test output'


def test_exec_git_branch(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_exec_git_branch

    stdout = 'test output'.encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = exec_git_branch()
    assert ret == 'test output'


def test_exec_git_annex_whereis(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_exec_git_annex_whereis

    stdout = 'test output'.encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = exec_git_annex_whereis()
    assert ret == 'test output'


def test_git_annex_add(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_git_annex_add

    stdout = 'test output'.encode(encoding='utf-8')
    mock_obj = mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = git_annex_add('add_file.txt')
    assert ret == 'test output'
    expected_command = 'git annex add "add_file.txt"'
    mock_obj.assert_called_with(expected_command, cwd=HOME_PATH, raise_error=False)


def test_git_add(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_git_add

    stdout = 'test output'.encode(encoding='utf-8')
    mock_obj = mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = git_add('add_file.txt')
    assert ret == 'test output'
    expected_command = 'git add "add_file.txt"'
    mock_obj.assert_called_with(expected_command, cwd=HOME_PATH, raise_error=False)


def test_git_commmit(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_git_commmit

    stdout = 'test output'.encode(encoding='utf-8')
    mock_obj = mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = git_commmit('test message')
    assert ret == 'test output'
    expected_command = 'git commit -m "test message"'
    mock_obj.assert_called_with(expected_command, cwd=HOME_PATH, raise_error=False)


def test_git_mv(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_git_mv

    stdout = 'test output'.encode(encoding='utf-8')
    mock_obj = mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = git_mv('test_src', 'test_dest')
    assert ret == 'test output'
    expected_command = 'git mv "test_src" "test_dest"'
    mock_obj.assert_called_with(expected_command, cwd=HOME_PATH, raise_error=False)


def test_git_ls_files(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_git_ls_files

    stdout = 'test output'.encode(encoding='utf-8')
    mock_obj = mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = git_ls_files('test_path')
    assert ret == 'test output'
    expected_command = 'git ls-files -s "test_path"'
    mock_obj.assert_called_with(expected_command, cwd=HOME_PATH, raise_error=False)


def test_disable_encoding_git(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_disable_encoding_git

    mocker.patch('nb_libs.utils.common.common.exec_subprocess')
    # エラーが発生しなければOK
    disable_encoding_git()


def test_enable_encoding_git(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_enable_encoding_git

    mocker.patch('nb_libs.utils.common.common.exec_subprocess')
    # エラーが発生しなければOK
    enable_encoding_git()


def test_git_annex_lock(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_git_annex_lock

    stdout = 'test output'.encode(encoding='utf-8')
    mock_obj = mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = git_annex_lock('test_path')
    assert ret == 'test output'
    expected_command = 'git annex lock test_path'
    mock_obj.assert_called_with(expected_command, raise_error=False)


def test_git_annex_unlock(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_git_annex_unlock

    stdout = 'test output'.encode(encoding='utf-8')
    mock_obj = mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = git_annex_unlock('test_path')
    assert ret == 'test output'
    expected_command = 'git annex unlock test_path'
    mock_obj.assert_called_with(expected_command, raise_error=False)


def test_git_annex_remove_metadata(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_git_annex_remove_metadata

    stdout = 'test output'.encode(encoding='utf-8')
    mock_obj = mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = git_annex_remove_metadata('test_path')
    assert ret == 'test output'
    expected_command = 'git annex metadata --remove-all test_path'
    mock_obj.assert_called_with(expected_command)


def test_git_annex_unannex(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_git_annex_unannex

    stdout = 'test output'.encode(encoding='utf-8')
    mock_obj = mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = git_annex_unannex('test_path')
    assert ret == 'test output'
    expected_command = 'git annex unannex test_path'
    mock_obj.assert_called_with(expected_command)


def test_git_annex_resolvemerge(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_git_annex_resolvemerge

    mocker.patch('nb_libs.utils.common.common.exec_subprocess')
    # エラーが発生しなければOK
    git_annex_resolvemerge()


def test_git_annex_untrust(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_git_annex_untrust

    stdout = 'test output'.encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = git_annex_untrust()
    assert ret == 'test output'


def test_git_annex_trust(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_git_annex_trust

    stdout = 'test output'.encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = git_annex_trust()
    assert ret == 'test output'


def test_git_annex_whereis(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_git_annex_whereis

    stdout = 'test output'.encode(encoding='utf-8')
    mock_obj = mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = git_annex_whereis('test_path', 'test_exec_path')
    assert ret == 'test output'
    expected_command = 'git annex whereis test_path --json'
    mock_obj.assert_called_with(expected_command, cwd='test_exec_path')


def test_git_annex_metadata_add_minetype_sha256_contentsize(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_git_annex_metadata_add_minetype_sha256_contentsize

    mock_obj = mocker.patch('nb_libs.utils.common.common.exec_subprocess')
    git_annex_metadata_add_minetype_sha256_contentsize('test_path', 'test_type', 'test_sha256', 0, 'test_exec_path')
    expected_command = 'git annex metadata "test_path" -s mime_type=test_type -s sha256=test_sha256 -s content_size=0'
    mock_obj.assert_called_with(expected_command, cwd='test_exec_path')


def test_git_annex_metadata_add_sd_date_published(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_git_annex_metadata_add_sd_date_published

    mock_obj = mocker.patch('nb_libs.utils.common.common.exec_subprocess')
    git_annex_metadata_add_sd_date_published('test_path', '2023-01-01', 'test_exec_path')
    expected_command = 'git annex metadata "test_path" -s sd_date_published=2023-01-01'
    mock_obj.assert_called_with(expected_command, cwd='test_exec_path')


def test_get_conflict_filepaths(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_get_conflict_filepaths

    # 変更なし
    stdout = '\n'.join(git_status_no_change).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_conflict_filepaths()
    assert ret == []

    # 変更あり
    stdout = '\n'.join(git_status_modified).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_conflict_filepaths()
    assert ret == []

    # ステージング済み
    stdout = '\n'.join(git_status_staging).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_conflict_filepaths()
    assert ret == []

    # 競合あり
    stdout = '\n'.join(git_status_conflict).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_conflict_filepaths()
    assert ret == ['dir1/add2 exist space.py', 'dir1/add2.py', 'dir1/modified2 exist space.py', 'dir1/modified2.py']


def test_get_modified_filepaths(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_get_modified_filepaths

    # 変更なし
    stdout = '\n'.join(git_status_no_change).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_modified_filepaths()
    assert ret == []

    # 変更あり
    stdout = '\n'.join(git_status_modified).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_modified_filepaths()
    assert ret == ['dir1/modified exist space.py', 'dir1/modified.py']

    # ステージング済み
    stdout = '\n'.join(git_status_staging).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_modified_filepaths()
    assert ret == []

    # 競合あり
    stdout = '\n'.join(git_status_conflict).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_modified_filepaths()
    assert ret == []


def test_get_delete_filepaths(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_get_delete_filepaths

    # 変更なし
    stdout = '\n'.join(git_status_no_change).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_delete_filepaths()
    assert ret == []

    # 変更あり
    stdout = '\n'.join(git_status_modified).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_delete_filepaths()
    assert ret == ['dir1/delete exist space.py', 'dir1/delete.py']

    # ステージング済み
    stdout = '\n'.join(git_status_staging).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_delete_filepaths()
    assert ret == []

    # 競合あり
    stdout = '\n'.join(git_status_conflict).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_delete_filepaths()
    assert ret == []


def test_get_annex_content_file_path_list(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_get_annex_content_file_path_list

    output_git_annex_whereis = [
        '{"file": "dir1/test_file1.txt"}',
        '{"file": "dir1/test_file2.txt"}',
        '{"file": "dir2/test_file3.txt"}',
        '',
    ]
    stdout = '\n'.join(output_git_annex_whereis).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_annex_content_file_paht_list()
    assert ret == ['dir1/test_file1.txt', 'dir1/test_file2.txt', 'dir2/test_file3.txt']


def test_get_remote_annex_variant_path(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_get_remote_annex_variant_path

    stdout = '\n'.join(git_status_staging).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_remote_annex_variant_path(['dir1/add exist space.py', 'dir1/add.py'])
    assert ret == ['dir1/add exist space.variant-.py', 'dir1/add.variant-.py']


def test_get_local_object_hash_by_path(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_get_local_object_hash_by_path

    # 正常ケース
    output_git_ls_files = [
        '100644 6277bb8e29c3cb9c00cfb9d8f0b8908bc5ef8a53 1	dir1/test_conflict.py',
        '100644 eb668bc1bc159a297af7caea12e729ff3702d4a7 2	dir1/test_conflict.py',
        '100644 7f543fb26cbfbf10e0e0ab694cfdab76b4e212ca 3	dir1/test_conflict.py',
    ]
    stdout = '\n'.join(output_git_ls_files).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_local_object_hash_by_path('dir1/test_conflict.py')
    assert ret == 'eb668bc1bc159a297af7caea12e729ff3702d4a7'

    # 指定したパスが存在しない
    stdout = ''.encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_local_object_hash_by_path('dir1/test_conflict.py')
    assert ret == ''


def test_get_multi_local_object_hash_by_path(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_get_multi_local_object_hash_by_path

    output_git_ls_files1 = [
        '100644 6277bb8e29c3cb9c00cfb9d8f0b8908bc5ef8a53 1	dir1/test_conflict1.py',
        '100644 eb668bc1bc159a297af7caea12e729ff3702d4a7 2	dir1/test_conflict1.py',
        '100644 7f543fb26cbfbf10e0e0ab694cfdab76b4e212ca 3	dir1/test_conflict1.py',
    ]
    output_git_ls_files2 = [
        '100644 7bad6b79f0d9c0ba4f21db4981d1079e0027d762 1	dir2/test_conflict2.py',
        '100644 6dba6c13171ab309cdd2244defe9a244ba52b6d4 2	dir2/test_conflict2.py',
        '100644 0eb05f6acc801ba003e1d9bbdce3c5d9db725f46 3	dir2/test_conflict2.py',
    ]
    stdout1 = '\n'.join(output_git_ls_files1).encode(encoding='utf-8')
    stdout2 = '\n'.join(output_git_ls_files2).encode(encoding='utf-8')
    side_effect = [(stdout1, None, None), (stdout2, None, None)]    # 1回目と2回目で実行結果を変える
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', side_effect=side_effect)

    ret = get_multi_local_object_hash_by_path(['dir1/test_conflict1.py', 'dir2/test_conflict2.py'])
    assert ret == [
        'eb668bc1bc159a297af7caea12e729ff3702d4a7',
        '6dba6c13171ab309cdd2244defe9a244ba52b6d4'
    ]


def test_is_conflict(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_is_conflict

    # 変更なし
    stdout = '\n'.join(git_status_no_change).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    assert not is_conflict()

    # 変更あり
    stdout = '\n'.join(git_status_modified).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    assert not is_conflict()

    # ステージング済み
    stdout = '\n'.join(git_status_staging).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    assert not is_conflict()

    # 競合あり
    stdout = '\n'.join(git_status_conflict).encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    assert is_conflict()


def test_get_remote_url(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_get_remote_url

    stdout = 'https://test.github-domain/test_user/test_repo.git\n'.encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_remote_url()
    assert ret == 'https://test.github-domain/test_user/test_repo.git'


def test_get_current_branch(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/git/test_git_module.py::test_get_current_branch

    # 正常ケース
    stdout = '* develop'.encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_current_branch()
    assert ret == 'develop'

    # 取得失敗のケース
    stdout = ''.encode(encoding='utf-8')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess', return_value=(stdout, None, None))
    ret = get_current_branch()
    assert ret == ''
