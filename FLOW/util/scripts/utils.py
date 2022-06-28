import json


def fetch_param_file_path() -> str:
    return '/home/jovyan/WORKFLOWS/FLOW/param_files/params.json'


def fetch_monitoring_param_file_path() -> str:
    return '/home/jovyan/WORKFLOWS/FLOW/param_files/monitoring_params.json'


def reflect_monitoring_results(monitoring_item, isOK: bool) -> None:
    # モニタリング観点名とnotebookへのパスとを取得
    path_params = fetch_param_file_path()
    params = {}
    with open(path_params, 'r') as f:
        params = json.load(f)

    nb = params['monitoring'][monitoring_item]
    # nb['name']: モニタリング観点名(str)
    # nb['path']: Notebookへのパス(str)

    # READMEの内容を取得する
    with open("/home/jovyan/README.md", "r") as f:
        readme = f.read()
    point1 = readme.find("| " + nb['name'] + " |")
    output = readme[:point1]

    # 該当する行を書き換え
    output += "| " + nb['name'] + " | [" + ("OK" if isOK else "NG") + "](" + nb['path'] + ") |"

    point2 = readme[point1:].find("\n")
    output += readme[point1 + point2:]

    with open("/home/jovyan/README.md", "w") as f:
        f.write(output)
