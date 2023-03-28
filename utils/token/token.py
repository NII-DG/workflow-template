""" .token.jsonファイル操作クラス
"""

import os
import json

def get_ginfork_token():
    """$HOME/.token.jsonからginfork_tokenを取得する。
    RETURN
    -----------------
    ginfork_token : str
        Description : token for gin-fork
    """
    os.chdir(os.environ['HOME'])
    file_path = '.token.json'
    with open(file_path, 'r') as f:
        data = json.load(f)
    ginfork_token = data['ginfork_token']
    return ginfork_token