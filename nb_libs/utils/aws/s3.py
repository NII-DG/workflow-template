import requests, os
import nb_libs.utils.message.message as mess
import nb_libs.utils.path.path as path

def access_s3_url(url) -> str:
    """S3オブジェクトURLの検証を行う

    Return:
        エラーメッセージ

    """
    msg = ""
    try:
        response = requests.head(url)
        if response.status_code == 200:
            pass
        elif response.status_code == 404 or response.status_code == 400:
            msg = mess.get('from_s3', 'wrong_url')
        elif response.status_code == 403:
            msg = mess.get('from_s3', 'private_object')
        else:
            msg = mess.get('from_s3', 'exception')
    except requests.exceptions.RequestException:
        msg = mess.get('from_s3', 'wrong_url')
    return msg

def validate_input_path(input_paths:list, experiment_title:str):
    '''格納先のパスの検証を行う
        
        Args:
            input_paths
            experiment_title

    '''
    path_set = set()
    for input_path, input_url in range(input_paths):
        err_msg = ''

        # input_data/, source/から始まること
        if not input_path.startswith('input_data/') and not input_path.startswith('source/'):
            err_msg = mess.get('from_s3', 'start_with')

        # 'input_data/', 'source/'だけではないこと
        elif input_path == 'input_data/' or input_path == 'source/':
            err_msg = input_path + mess.get('from_s3', 'after_dir')

        # /で終わらないこと
        elif input_path.endswith('/'):
            err_msg = mess.get('from_s3', 'end_slash')

        # \がないこと
        elif '\\' in input_path:
            err_msg = mess.get('from_s3', 'backslash')

        # 拡張子が一致すること
        elif os.path.splitext(input_path)[1] != os.path.splitext(input_url)[1]:
            err_msg = input_path + mess.get('from_s3', 'different_ext')

        # 既存のファイルと重複がないこと
        elif os.path.isfile(path.create_experiments_sub_path(experiment_title, input_path)):
            err_msg = input_path + mess.get('from_s3', 'already_exist')

        # input_path内での重複がないこと
        elif input_path in path_set:
            err_msg = mess.get('from_s3', '')

        path_set.add(input_path)
        
    return err_msg
    