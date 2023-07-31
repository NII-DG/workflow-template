'''全般的な例外のモジュール'''

class DidNotFinishError(Exception):
    '''上のセルが未実行の場合に発生する'''
    pass

class UnexpectedError(Exception):
    '''予想外のエラーが発生した場合'''
    pass

class DGTaskError(Exception):
    '''タスクNotebookのコードセルで例外で処理停止しなければならないエラーが発生した場合'''
    pass

class ExecCmdError(Exception):
    '''コマンド実行エラー'''
    pass

class NoValueInDgFileError(Exception):
    '''タスクNotebookのコードセルで例外で処理停止しなければならないエラーが発生した場合'''
    pass