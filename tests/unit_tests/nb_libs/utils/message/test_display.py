from nb_libs.utils.message.display import (
    creat_html_msg,
    creat_html_msg_info_p,
    creat_html_msg_err_p,
    display_html_msg,
    display_log,
    display_msg,
    display_info,
    display_err,
    display_warm,
    display_debug,
)


def test_creat_html_msg():
    # pytest -v -s tests/unit_tests/nb_libs/utils/message/test_display.py::test_creat_html_msg

    html_msg = creat_html_msg(msg='test_msg', fore='#000000', back='#FFFFFF', tag='p')
    assert html_msg == "<p style='color:#000000;background-color:#FFFFFF;'>test_msg</p>"

    html_msg = creat_html_msg(msg='test_msg', fore='#000000', tag='p')
    assert html_msg == "<p style='color:#000000'>test_msg</p>"

    html_msg = creat_html_msg(msg='test_msg', back='#FFFFFF', tag='p')
    assert html_msg == "<p style='background-color:#FFFFFF'>test_msg</p>"

    html_msg = creat_html_msg()
    assert html_msg == "<h1 style=''></h1>"


def test_creat_html_msg_info_p():
    # pytest -v -s tests/unit_tests/nb_libs/utils/message/test_display.py::test_creat_html_msg_info_p

    html_msg = creat_html_msg_info_p('test_msg')
    assert html_msg == "<p style='background-color:#9eff9e'>test_msg</p>"


def test_creat_html_msg_err_p():
    # pytest -v -s tests/unit_tests/nb_libs/utils/message/test_display.py::test_creat_html_msg_err_p

    html_msg = creat_html_msg_err_p('test_msg')
    assert html_msg == "<p style='background-color:#ffa8a8'>test_msg</p>"


def test_display_html_msg():
    # pytest -v -s tests/unit_tests/nb_libs/utils/message/test_display.py::test_display_html_msg

    # notebookの出力に表示する関数なので表示内容は結合テストで確認する。
    # 単体テストではエラーが起きなければOK
    display_html_msg()


def test_display_log():
    # pytest -v -s tests/unit_tests/nb_libs/utils/message/test_display.py::test_display_log

    # notebookの出力に表示する関数なので表示内容は結合テストで確認する。
    # 単体テストではエラーが起きなければOK
    display_log('test_msg')


def test_display_msg():
    # pytest -v -s tests/unit_tests/nb_libs/utils/message/test_display.py::test_display_msg

    # notebookの出力に表示する関数なので表示内容は結合テストで確認する。
    # 単体テストではエラーが起きなければOK
    display_msg('test_msg')


def test_display_info():
    # pytest -v -s tests/unit_tests/nb_libs/utils/message/test_display.py::test_display_info

    # notebookの出力に表示する関数なので表示内容は結合テストで確認する。
    # 単体テストではエラーが起きなければOK
    display_info('test_msg')


def test_display_err():
    # pytest -v -s tests/unit_tests/nb_libs/utils/message/test_display.py::test_display_err

    # notebookの出力に表示する関数なので表示内容は結合テストで確認する。
    # 単体テストではエラーが起きなければOK
    display_err('test_msg')


def test_display_warm():
    # pytest -v -s tests/unit_tests/nb_libs/utils/message/test_display.py::test_display_warm

    # notebookの出力に表示する関数なので表示内容は結合テストで確認する。
    # 単体テストではエラーが起きなければOK
    display_warm('test_msg')


def test_display_debug():
    # pytest -v -s tests/unit_tests/nb_libs/utils/message/test_display.py::test_display_debug

    # notebookの出力に表示する関数なので表示内容は結合テストで確認する。
    # 単体テストではエラーが起きなければOK
    display_debug('test_msg')
