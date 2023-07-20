import os
import shutil
from IPython.display import display, SVG
from ..path import path


def display_flow(flow_type:str):
    """フロー図を表示する

    Args:
        flow_type (str): フローの種別('research' or 'experiment')
    """
    if flow_type == 'research':
        import research as util
        notebook_dir = path.RES_DIR_PATH
    elif flow_type == 'experiment':
        import experiment as util
        notebook_dir = path.EXP_DIR_PATH
    else:
        raise ValueError

    diag_file_name = flow_type + '_notebooks.diag'
    svg_file_name = flow_type + '_notebooks.svg'
    orig_diag_path = os.path.join(path.DATA_PATH, 'flow', diag_file_name)

    diag_path = os.path.join(path.SYS_PATH, diag_file_name)
    svg_path = os.path.join(path.SYS_PATH, svg_file_name)

    if not os.path.isdir(path.SYS_PATH):
        os.mkdir(path.SYS_PATH)

    if not os.path.isfile(diag_path):
        shutil.copy(orig_diag_path, diag_path)

    util.generate_svg_diag(output=svg_path, diag=diag_path, dir_util=notebook_dir)
    display(SVG(filename=svg_path))
