# -*- coding: utf-8 -*-
import re
import sys
from subprocess import run
from tempfile import TemporaryDirectory
from pathlib import Path
from lxml import etree
from nbformat import read, NO_CONVERT
from itertools import chain, zip_longest
from ..path import path as dg_path


title_font_size = 10
item_font_size = 7
head_margin = 2
text_margin = 1
title_font_color = 'rgb(255,140,0)'
text_font_color = 'rgb(0,0,0)'

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
        'path': nb_path.as_posix(),
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


def generate_svg_diag(
        output='WORKFLOWS/data/flow/experiment_notebooks.svg',
        diag='WORKFLOWS/data/flow/experiment_notebooks.diag',
        dir_util='WORKFLOWS/notebooks/experimnet',
        font='.fonts/ipag.ttf',
):
    with TemporaryDirectory() as workdir:
        skeleton = Path(workdir) / 'skeleton.svg'
        _generate_skeleton(skeleton, Path(diag), Path(font))
        _embed_detail_information(Path(output), skeleton, Path(dir_util))
        return output

def _generate_skeleton(output, diag, font):
    run(['blockdiag', '-f', font, '-Tsvg', '-o', output, diag], check=True)

def setup_python_path():
    ver = sys.version_info
    lib_path = f'~/.local/lib/python{ver.major}.{ver.minor}/site-packages'
    lib_path = str(Path(lib_path).expanduser())
    if lib_path not in sys.path:
        sys.path.append(lib_path)

def _embed_detail_information(output, skeleton, dir_util):
    # Notebookのヘッダ取得
    nb_headers = _get_notebook_headers(dir_util)

    # 雛形の読み込み
    tree = etree.parse(str(skeleton))

    # 雛形をNotebook情報で置き換え
    for elem in list(tree.findall(SVG_TEXT)):
        if _is_target_rect(elem, nb_headers.keys()):
            nb_name = _find_matching_notebook(nb_headers.keys(), elem.text)
            _embed_info_in_one_rect(elem, nb_headers, nb_name)

    # SVGの保存
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open(mode='wb') as f:
        f.write(etree.tostring(tree, method='xml', pretty_print=True))

def _is_target_rect(elem, notebooks):
    return (
        elem.getprevious() is not None and
        elem.getprevious().tag == SVG_RECT and
        len(elem.text) > 0 and
        _find_matching_notebook(notebooks, elem.text) is not None)

def _find_matching_notebook(notebooks, title):
    for nb in notebooks:
        if nb.startswith(title):
            return nb

def _embed_info_in_one_rect(elem, nb_headers, nb_name):
    headers = nb_headers[nb_name]
    nb_file = nb_headers[nb_name]['path']
    nb_file = nb_file.replace(dg_path.EXP_DIR_PATH, '.')
    rect_elem = elem.getprevious()
    rect = (
        (int(rect_elem.attrib['x']), int(rect_elem.attrib['y'])),
        (int(rect_elem.attrib['width']), int(rect_elem.attrib['height'])))
    childpos = elem.getparent().index(elem)
    parent_elem = elem.getparent()
    remove_texts(elem)
    title = headers['title']['text']
    if elem.text.find(':') >= 0:
        title = title + ' - ' + elem.text.split(':')[1]
    line_num = insert_title(parent_elem, childpos, rect, title, str(nb_file))
    insert_headers(parent_elem, childpos, rect, headers['headers'], line_num)

def remove_texts(elem):
    old_text = elem
    while old_text is not None:
        if (old_text.getnext() is not None and
                old_text.getnext().tag == SVG_TEXT):
            next_text = old_text.getnext()
        else:
            next_text = None
        old_text.getparent().remove(old_text)
        old_text = next_text

def insert_title(parent_elem, childpos, rect, title, link):
    height_title = (
        text_margin + (title_font_size + text_margin) * 2 + head_margin * 2)
    lines = split_title(title)
    if len(lines) == 2:
        text_elem = create_text(rect, title_font_size, font_weight='bold', font_color=title_font_color)
        text_elem.text = lines[0]
        text_elem.attrib['y'] = str(
                rect[0][1] + head_margin + text_margin + title_font_size)
        text_elems = [text_elem]

        text_elem = create_text(rect, title_font_size, font_weight='bold', font_color=title_font_color)
        text_elem.text = lines[1]
        text_elem.attrib['y'] = str(
                rect[0][1] + height_title - text_margin - head_margin)
        text_elems.append(text_elem)
    else:
        text_elem = create_text(rect, title_font_size, font_weight='bold', font_color=title_font_color)
        text_elem.text = title
        text_elem.attrib['y'] = str(
                rect[0][1] + height_title // 2 + title_font_size // 2)
        text_elems = [text_elem]

    parent_elem.insert(childpos, create_anchor(text_elems, link))
    return len(lines)

def insert_headers(parent_elem, childpos, rect, headers, title_lines):
    offset_y = (
        text_margin +
        (title_font_size + text_margin) * (title_lines + 1) +
        head_margin * 2 + text_margin)
    for i, header in enumerate(headers):
        text_elem = create_text(rect, item_font_size, font_color=text_font_color)
        text_elem.text = header['text']
        text_elem.attrib['y'] = str(
                rect[0][1] + offset_y + (item_font_size + text_margin) * i +
                item_font_size)
        parent_elem.insert(childpos, text_elem)

def split_title(title):
    if u'：' in title:
        return [title[:title.index(u'：') + 1], title[title.index(u'：') + 1:]]
    elif len(title) >= 15:
        words = re.split(r'([-(（])', title, 1)
        ret = words[0:1] + [''.join(x) for x in zip(words[1::2], words[2::2])]
        return [re.sub(r'^--', '- ', x) for x in ret]
    else:
        return [title]

def create_text(rect, font_size, font_color, font_weight='normal', font_style='normal'):
    text_elem = etree.Element(SVG_TEXT)
    text_elem.attrib['fill'] = font_color
    text_elem.attrib['font-family'] = 'sans-serif'
    text_elem.attrib['font-size'] = str(font_size)
    text_elem.attrib['font-style'] = font_style
    text_elem.attrib['font-weight'] = font_weight
    text_elem.attrib['font-anchor'] = 'middle'
    text_elem.attrib['x'] = str(rect[0][0] + text_margin)
    text_elem.attrib['width'] = str(rect[1][0] - text_margin * 2)
    return text_elem

def create_anchor(elems, link):
    a_elem = etree.Element('a')
    a_elem.attrib['{http://www.w3.org/1999/xlink}href'] = link
    for elem in elems:
        a_elem.append(elem)
    return a_elem


# refs: https://note.nkmk.me/python-if-name-main/
# maDMP.ipynbからコマンドライン引数でdiagファイルのパスが渡されてくる
if __name__ == '__main__':
    generate_svg_diag(diag=sys.argv[1])
