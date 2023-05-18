import subprocess


def get_AND_elements(list_a, list_b :list)->list:

    and_elements = set(list_a) & set(list_b)
    return list(and_elements)


def exec_subprocess(cmd: str, raise_error=True):
    child = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = child.communicate()
    rt = child.returncode
    if rt != 0 and raise_error:
        raise Exception(f"command return code is not 0. got {rt}. stderr = {stderr}")

    return stdout, stderr, rt