
import subprocess

def exec_subprocess(cmd: str, raise_error=True):
    '''
    コマンドを同期実行し、
    標準出力と標準エラー出力は最後にまとめて返却する
    raise_errorがTrueかつリターンコードが0以外の場合は例外を出す
    戻り値は3値のタプルで (標準出力(bytes型), 標準エラー出力(bytes型), リターンコード(int))
    '''
    child = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = child.communicate()
    rt = child.returncode
    if rt != 0 and raise_error:
        raise Exception(f"command return code is not 0. got {rt}. stderr = {stderr}")

    return stdout, stderr, rt