import panel as pn
from IPython.display import HTML, display
from ..message import message
import os

# def git_conflict_resolve_form(conflicted_git_path:list):
#     pn.extension()
#     button = prepare.create_button(name=message.get('conflict_helper', 'correction_complete'))

#     def validate(event):
#         button.value

#         pass

#     button.on_click(validate)
#     display(pn.Column(button))

# ファイルパスと確定ボタンの対を表すクラス
class FileConfirmationPair:
    def __init__(self, file_path):
        self.file_path = file_path
        self.confirm_button = pn.widgets.Button(name="確定")
        self.confirm_button.on_click(self.confirm_file)

        self.success_label = pn.widgets.StaticText(value="")

    def confirm_file(self, event):
        # ファイルパスの確認ロジックをここに実装（ファイルが存在するか確認するなど）
        # ここでは仮にファイルが存在するとする
        if self.file_path_exists():
            self.success_label.value = "成功"
        else:
            self.success_label.value = "失敗"

    def file_path_exists(self):
        # 実際のファイルパスの存在確認ロジックを実装
        # ここでは仮にファイルが存在するとする
        return os.path.exists(self.file_path)

def create_confirmation_form(file_paths):
    form_items = []
    for file_path in file_paths:
        pair = FileConfirmationPair(file_path)
        form_items.append(pn.Row(pair.confirm_button, pair.success_label))

    return display(pn.Column(*form_items))
