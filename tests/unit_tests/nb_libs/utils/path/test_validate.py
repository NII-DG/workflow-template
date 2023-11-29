
from nb_libs.utils.path.validate import validate_input_path


def test_validate_input_path(create_duplicate_file):
    # pytest -v -s tests/nb_libs/utils/path/test_validate.py::test_validate_input_path

    # input_data/, source/から始まること
    input = [
        ('output_data/file1.txt', 'experiments/old_package/input_data/file1.txt')
    ]
    ret = validate_input_path(input, 'new_package')
    assert ret == '格納先のファイルパスはinput_data/かsource/で始まる必要があります。修正後、再度クリックしてください。'

    # 'input_data/', 'source/'だけではないこと
    input = [
        ('input_data/', 'experiments/old_package/input_data/file1.txt')
    ]
    ret = validate_input_path(input, 'new_package')
    assert ret == 'input_data/ 以降が入力されていません。修正後、再度クリックしてください。'

    input = [
        ('source/', 'experiments/old_package/source/file1.txt')
    ]
    ret = validate_input_path(input, 'new_package')
    assert ret == 'source/ 以降が入力されていません。修正後、再度クリックしてください。'

    # /で終わらないこと
    input = [
        ('input_data/dir/', 'experiments/old_package/input_data/dir/file1.txt')
    ]
    ret = validate_input_path(input, 'new_package')
    assert ret == '格納先のファイルパスの末尾は"/"以外を入力してください。'

    # \がないこと
    input = [
        (r'input_data/dir\file1.txt', 'experiments/old_package/input_data/dir/file1.txt')
    ]
    ret = validate_input_path(input, 'new_package')
    assert ret == r'格納先のファイルパスに"\"は使えません。'

    # 拡張子が一致すること
    input = [
        ('input_data/dir/file1.jpg', 'experiments/old_package/input_data/dir/file1.txt')
    ]
    ret = validate_input_path(input, 'new_package')
    assert ret == 'input_data/dir/file1.jpg の拡張子が元のファイルと一致しません。修正後、再度クリックしてください。'

    # 既存のファイルと重複がないこと
    input = [
        ('input_data/dir/duplicate.txt', 'experiments/old_package/input_data/dir/duplicate.txt')
    ]
    ret = validate_input_path(input, 'new_package')
    assert ret == 'input_data/dir/duplicate.txt は既に存在するファイルです。修正後、再度クリックしてください。'

    # input_path内での重複がないこと
    input = [
        ('input_data/dir/file1.txt', 'experiments/old_package/input_data/dir/file1.txt'),
        ('input_data/dir/file1.txt', 'experiments/old_package/input_data/dir/file2.txt'),
    ]
    ret = validate_input_path(input, 'new_package')
    assert ret == 'ファイル名: input_data/dir/file1.txt が重複しています。修正後、再度クリックしてください。'

    # 正常ケース
    input = [
        ('input_data/dir/file1.txt', 'experiments/old_package/input_data/dir/file1.txt'),
        ('input_data/dir/file2.txt', 'experiments/old_package/input_data/dir/file2.txt'),
    ]
    ret = validate_input_path(input, 'new_package')
    assert ret == ''
