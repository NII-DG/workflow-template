'''全般的な例外のモジュール'''

class DidNotFinishError(Exception):
    '''上のセルが未実行の場合に発生する'''
    pass

class UnexpectedError(Exception):
    '''予想外のエラーが発生した場合'''
    pass