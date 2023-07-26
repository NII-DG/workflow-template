'''パスの検証を行うモジュール'''
import os
from ..message import message
from ..path import path

def validate_input_path(input_paths:list, experiment_title:str) -> str:
    '''格納先パスの検証を行う
        
        Args:
            input_paths(list): (input_path, input_url)のリスト
            
            experiment_title(str): 実験パッケージ名

        Returns:
            エラーメッセージ

    '''
    path_set = set()
    for input_path, input_url in input_paths:

        # input_data/, source/から始まること
        if not input_path.startswith('input_data/') and not input_path.startswith('source/'):
            return message.get('validate', 'start_with')

        # 'input_data/', 'source/'だけではないこと
        elif input_path == 'input_data/' or input_path == 'source/':
            return message.get('validate', 'after_dir').format(input_path)

        # /で終わらないこと
        elif input_path.endswith('/'):
            return message.get('validate', 'end_slash')

        # \がないこと
        elif '\\' in input_path:
            return message.get('validate', 'backslash')

        # 拡張子が一致すること
        elif os.path.splitext(input_path)[1] != os.path.splitext(input_url)[1]:
            return message.get('validate', 'different_ext').format(input_path)

        # 既存のファイルと重複がないこと
        elif os.path.isfile(path.create_experiments_with_subpath(experiment_title, input_path)):
            return message.get('validate', 'already_exist').format(input_path)

        # input_path内での重複がないこと
        elif input_path in path_set:
            return message.get('validate', 'duplicate_path').format(input_path)

        path_set.add(input_path)
        
    return ""