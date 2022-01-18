# -*- coding: utf-8 -*-

import os
import re
import sys
import shutil
from subprocess import run, CalledProcessError
from tempfile import TemporaryDirectory
from pathlib import Path
from lxml import etree
from nbformat import read, NO_CONVERT
from itertools import chain, zip_longest
from jinja2 import Template
from datetime import datetime

title_font_size = 11
item_font_size = 9
head_margin = 3
text_margin = 2

SVG_TEXT = '{http://www.w3.org/2000/svg}text'
SVG_RECT = '{http://www.w3.org/2000/svg}rect'


def parse_headers(nb_path):
    nb = read(str(nb_path), as_version=NO_CONVERT)

    # Notebookのセルからmarkdownの部分を取り出し、行ごとのリストにする
    lines = [
        line.strip()
        for line in chain.from_iterable(
            cell['source'].split('\n')
            for cell in nb.cells
            if cell['cell_type'] == 'markdown'
        )
        if len(line.strip()) > 0 and not line.startswith('---')
    ]

    # h1, h2 の行とその次行の最初の１文を取り出す
    headers = [
        (' '.join(line0.split()[1:]),
         line1.split("。")[0] if line1 is not None else '')
        for (line0, line1) in zip_longest(lines, lines[1:])
        if line0.startswith('# ') or line0.startswith('## ')
    ]
    # 最初の見出しはtitle, 残りはheadersとして返す
    return {
        'title': {
            'text': _to_title_text(nb_path, headers[0][0]),
            'summary': headers[0][1],
        },
        'headers': [
            {
                'text': text,
                'summary': (
                    summary if not re.match(r'(?:#|!\[)', summary) else ''),
            }
            for (text, summary) in headers[1:]
        ],
    }

def _to_title_text(nb_path, text):
    no = nb_path.name.split('-')[0]
    title = text if not text.startswith('About:') else text[6:]
    return f'{title}'

def _get_notebook_headers(nb_dir):
    return dict([
        (nb.name, parse_headers(nb))
        for nb in nb_dir.glob("*.ipynb")
    ])

def notebooks_toc(nb_dir):
    nb_headers = sorted(
        _get_notebook_headers(Path(nb_dir)).items(),
        key=lambda x: x[0])
    
    return "\n".join(chain.from_iterable([
        [
            f'* [{headers["title"]["text"]}]({nb_dir}/{str(nb)})'
        ] + list(chain.from_iterable([
            [
                f'    - {header["text"]}',
                (f'      - {header["summary"]}'
                 if len(header["summary"]) > 0 else ''),
            ]
            for header in headers['headers']
        ]))
        for nb, headers in nb_headers
    ]))

import json

JSON = ""
def load_json(PATH):
    with open(PATH) as f:
        JSON = json.load(f)
        return JSON
    
    
def setup_diag():
    setup_blockdiag()
    setup_lxml()

def setup_lxml():
    if not check_lxml():
        install_lxml()
    return check_lxml()


def check_lxml():
    try:
        import lxml
        return True
    except ModuleNotFoundError:
        return False


def install_lxml():
    run('pip install -q --user lxml', shell=True)
    setup_python_path()

    
def setup_blockdiag():
    if not check_blockdiag():
        install_blockdiag()
    return check_blockdiag()

def check_blockdiag():
    try:
        run('blockdiag -h', shell=True, check=True)
        return True
    except CalledProcessError:
        return False

def install_blockdiag():
    run('pip install -q --user blockdiag', shell=True)
    paths = os.environ['PATH'].split(':')
    local_bin = str(Path('~/.local/bin').expanduser())
    if local_bin not in paths:
        paths.append(local_bin)
        os.environ['PATH'] = ':'.join(paths)
    if not check_blockdiag():
        install_blockdiag()

def generate_svg_diag(
        output='images/notebooks.svg',
        diag='images/notebooks.diag',
        nb_dir='/home/jovyan/FLOW',
        font='/usr/share/fonts/truetype/fonts-japanese-gothic.ttf',
):
    with TemporaryDirectory() as workdir:
        skeleton = Path(workdir) / 'skeleton.svg'
        _generate_skeleton(skeleton, Path(diag), Path(font))
        _embed_detail_information(Path(output), skeleton, Path(nb_dir))
        return output

 def _generate_skeleton(output, diag, font):
    run(['blockdiag', '-f', font, '-Tsvg', '-o', output, diag], check=True)