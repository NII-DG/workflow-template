def fetch_param_file_path() -> str:
    return '/home/jovyan/WORKFLOW/FLOW/param_files/params.json'


def fetch_monitoring_param_file_path() -> str:
    return '/home/jovyan/WORKFLOW/FLOW/param_files/monitoring_params.json'


def reflect_monitoring_results(item_name: str, isOK: bool) -> None:
    with open("/home/jovyan/README.md", "r") as f:
        readme = f.read()

    point1 = readme.find("| " + item_name + " |")
    output = readme[:point1]

    # FIXME: リンク先が全て"base_monitor_data_size.ipynb"になる点を修正したい
    output += "| " + item_name + " | [" + ("OK" if isOK else "NG") + "](./WORKFLOW/FLOW/02_experimental_phase/base_monitor_data_size.ipynb) |"

    point2 = readme[point1:].find("\n")
    output += readme[point1 + point2:]

    with open("/home/jovyan/README.md", "w") as f:
        f.write(output)
