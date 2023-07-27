import os
import shutil
from IPython.display import display, SVG
from ..path import path


diag_file_name = '{}_notebooks.diag'
svg_file_name = '{}_notebooks.svg'


def orig_diag_file_path(flow_type):
    return os.path.join(path.DATA_PATH, 'flow', diag_file_name).format(flow_type)


def diag_file_path(flow_type):
    return os.path.join(path.SYS_PATH, diag_file_name).format(flow_type)


def svg_file_path(flow_type):
    return os.path.join(path.SYS_PATH, svg_file_name).format(flow_type)


def display_flow(flow_type='research'):
    """フロー図を表示する

    Args:
        flow_type (str): フローの種別('research' or 'experiment')
    """
    if flow_type == 'research':
        from . import research as util
        notebook_dir = path.RES_DIR_PATH
    elif flow_type == 'experiment':
        from . import experiment as util
        notebook_dir = path.EXP_DIR_PATH
    else:
        raise ValueError

    orig_diag_path = orig_diag_file_path(flow_type)
    diag_path = diag_file_path(flow_type)
    svg_path = svg_file_path(flow_type)

    if not os.path.isdir(path.SYS_PATH):
        os.mkdir(path.SYS_PATH)

    if not os.path.isfile(diag_path):
        shutil.copy(orig_diag_path, diag_path)

    font_path = os.path.join(path.HOME_PATH, '.fonts/ipag.ttf')
    util.generate_svg_diag(output=svg_path, diag=diag_path, dir_util=notebook_dir, font=font_path,)
    display(SVG(filename=svg_path))


def put_mark(flow_type, name, mark):
    """フロー図にマークをつける

    Args:
        flow_type (str): フローの種別 ('research' or 'experiment')
        name (str): ノートブック名 (拡張子なし)
        mark (str): マークに表示する文字
    """

    diag_path = diag_file_path(flow_type)
    find = f'"{name}"[fontsize = 10];'
    replace = f'"{name}"[numbered = {mark}, fontsize = 10];'

    with open(diag_path, 'r') as f:
        s = f.read()

    with open(diag_path, 'w') as f:
        s = s.replace(find, replace)
        f.write(s)