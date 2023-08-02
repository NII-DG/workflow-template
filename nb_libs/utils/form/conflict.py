import panel as pn
from ..message import message, display as md
from ..common import common
from ..path import display as pd
from IPython.display import HTML, display

import os

# def git_conflict_resolve_form(conflicted_git_path:list):
#     pn.extension()
#     button = prepare.create_button(name=message.get('conflict_helper', 'correction_complete'))

#     def validate(event):
#         button.value

#         pass

#     button.on_click(validate)
#     display(pn.Column(button))


conflict_resolve_form_whole_msg = pn.pane.HTML()
# ファイルパスと確定ボタンの対を表すクラス
class GitFileResolvePair:
    def __init__(self, index, target_file_path:str, all_paths:list):
        self.file_path = target_file_path
        self.all_paths = all_paths

        self.confirm_button = pn.widgets.Button(name=message.get('conflict_helper', 'correction_complete'), button_type='primary')
        self.confirm_button.on_click(self.confirm_resolve)
        self.confirm_button.width = 200

        title = f'{index}：{self.file_path}'
        link = f'../../../../edit/{self.file_path}'
        link_html = pd.create_link(url=link, title=title)
        self.label = pn.pane.HTML(link_html)

    def confirm_resolve(self, event):
        # Confirm that the file has been edited

        # Check the status of all edits
        pass

def git_conflict_resolve_form(file_paths):
    pn.extension()
    form_items = []
    for index, file_path in enumerate(common.sortFilePath(file_paths)):
        pair = GitFileResolvePair(index, file_path, file_paths)
        form_items.append(pn.Column(pair.label,pair.confirm_button))
    conflict_resolve_form_whole_msg.object = ''
    conflict_resolve_form_whole_msg.width = 900
    return display(pn.Column(*form_items, conflict_resolve_form_whole_msg))
