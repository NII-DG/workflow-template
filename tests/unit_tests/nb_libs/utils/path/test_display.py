from nb_libs.utils.path.display import (
    button_html,
    res_top_html,
    res_top_link,
    res_top_link_from_maDMP,
    exp_top_html,
    exp_top_link,
    create_link,
)


def test_button_html():
    # pytest -v -s tests/nb_libs/utils/path/test_display.py::test_button_html

    # デフォルト値の場合
    ret = button_html('https://test-domain/', 'test_message')
    expected = '<a style="color: #fff; font-size: 15px; "href="https://test-domain/" target="_self"><button style="width: 300px; height: 30px; border-radius: 5px; background-color: #2185d0; border: 0px none;">test_message</button></a>'
    assert ret == expected

    # 引数をすべて指定
    ret = button_html('https://test-domain/', 'test_message', '_blank', '#f00', '10px', '200px', '20px', '2px', '#ff00ff')
    expected = '<a style="color: #f00; font-size: 10px; "href="https://test-domain/" target="_blank" rel="noopener"><button style="width: 200px; height: 20px; border-radius: 2px; background-color: #ff00ff; border: 0px none;">test_message</button></a>'
    assert ret == expected


def test_res_top_html():
    # pytest -v -s tests/nb_libs/utils/path/test_display.py::test_res_top_html

    assert res_top_html()


def test_res_top_link():
    # pytest -v -s tests/nb_libs/utils/path/test_display.py::test_res_top_link

    # エラーが発生しなければOK
    res_top_link()


def test_res_top_link_from_maDMP():
    # pytest -v -s tests/nb_libs/utils/path/test_display.py::test_res_top_link_from_maDMP

    # エラーが発生しなければOK
    res_top_link_from_maDMP()


def test_exp_top_html():
    # pytest -v -s tests/nb_libs/utils/path/test_display.py::test_exp_top_html

    assert exp_top_html()


def test_exp_top_link():
    # pytest -v -s tests/nb_libs/utils/path/test_display.py::test_exp_top_link

    # エラーが発生しなければOK
    exp_top_link()


def test_create_link():
    # pytest -v -s tests/nb_libs/utils/path/test_display.py::test_create_link

    # targetなし
    ret = create_link('https://test-domain/', 'test_title')
    expected = '<a href="https://test-domain/" target="_blank">test_title</a>'
    assert ret == expected

    # targetあり
    ret = create_link('https://test-domain/', 'test_title', '_self')
    expected = '<a href="https://test-domain/" target="_self">test_title</a>'
    assert ret == expected
