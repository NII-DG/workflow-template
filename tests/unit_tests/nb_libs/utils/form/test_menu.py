
from nb_libs.utils.form.menu import (
    create_dg_menu,
    dg_menu,
    html_res_name,
    html_exp_name,
    gin_link_html,
)

from tests.unit_tests.common.utils import UnitTestError


def test_create_dg_menu(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_menu.py::test_create_dg_menu

    mocker.patch('nb_libs.utils.git.git_module.get_remote_url', return_value='https://test.github-domain/test_user/test_repo.git')
    mocker.patch('nb_libs.utils.params.ex_pkg_info.get_current_experiment_title', return_value='test_title')
    mocker.patch('nb_libs.utils.gin.sync.update_repo_url')

    menu_selector, html_output = create_dg_menu(type='research')
    assert menu_selector.values == [1, 2, 3, 6]
    menu_selector.value = 3     # セレクトボックスの値変更イベントを発生させる
    assert html_output.object == '<a style="color: #fff; font-size: 15px; "href="./base_FLOW.ipynb" target="_self"><button style="width: 300px; height: 30px; border-radius: 5px; background-color: #2185d0; border: 0px none;">研究フロートップページに遷移する</button></a>'
    menu_selector.value = 2     # セレクトボックスの値変更イベントを発生させる
    assert html_output.object == "<h1 style='color:green'>研究リポジトリ名：test_repo</h1>"
    menu_selector.value = 1     # セレクトボックスの値変更イベントを発生させる
    assert html_output.object == ''

    menu_selector, html_output = create_dg_menu(type='experiment')
    assert menu_selector.values == [1, 4, 5, 6]
    menu_selector.value = 6     # セレクトボックスの値変更イベントを発生させる
    assert html_output.object == '<a style="color: #fff; font-size: 15px; "href="https://test.github-domain/test_user/test_repo.git" target="_blank" rel="noopener"><button style="width: 300px; height: 30px; border-radius: 5px; background-color: #2185d0; border: 0px none;">GIN-forkに遷移する</button></a>'
    menu_selector.value = 5     # セレクトボックスの値変更イベントを発生させる
    assert html_output.object == '<a style="color: #fff; font-size: 15px; "href="./experiment.ipynb" target="_self"><button style="width: 300px; height: 30px; border-radius: 5px; background-color: #2185d0; border: 0px none;">実験フロートップページに遷移する</button></a>'
    menu_selector.value = 4     # セレクトボックスの値変更イベントを発生させる
    assert html_output.object == "<h1 style='color:blue'>研究リポジトリ名：test_repo</h1><h1 style='color:blue'>実験パッケージ名：test_title</h1>"

    menu_selector, html_output = create_dg_menu(type='conflict')
    assert menu_selector.values == [1, 4, 6]
    menu_selector, html_output = create_dg_menu(type='research_top')
    assert menu_selector.values == [1, 2, 6]
    menu_selector, html_output = create_dg_menu(type='experiment_top')
    assert menu_selector.values == [1, 4, 6]


def test_dg_menu():
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_menu.py::test_dg_menu

    # エラーが発生しなければOK
    dg_menu()


def test_html_res_name(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_menu.py::test_html_res_name

    mocker.patch('nb_libs.utils.git.git_module.get_remote_url', return_value='https://test.github-domain/test_user/test_repo.git')

    # 正常ケース
    mocker.patch('nb_libs.utils.gin.sync.update_repo_url', return_value=False)
    ret = html_res_name()
    assert ret == "<h1 style='color:black'>研究リポジトリ名：test_repo</h1>"

    # リモートURLの更新失敗
    mocker.patch('nb_libs.utils.gin.sync.update_repo_url', side_effect=UnitTestError())
    ret = html_res_name()
    assert ret == "<h1 style='color:black'>研究リポジトリ名：test_repo</h1>"


def test_html_exp_name(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_menu.py::test_html_exp_name

    # 正常ケース
    mocker.patch('nb_libs.utils.params.ex_pkg_info.get_current_experiment_title', return_value='test_title')
    ret = html_exp_name()
    assert ret == "<h1 style='color:black'>実験パッケージ名：test_title</h1>"

    # パッケージ名取得失敗
    mocker.patch('nb_libs.utils.params.ex_pkg_info.get_current_experiment_title', return_value=None)
    ret = html_exp_name()
    assert ret == "<h1 style='color:black'>実験パッケージ名：-</h1>"

def test_gin_link_html(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_menu.py::test_gin_link_html

    mocker.patch('nb_libs.utils.git.git_module.get_remote_url', return_value='https://test.github-domain/test_user/test_repo.git')

    # 正常ケース
    mocker.patch('nb_libs.utils.gin.sync.update_repo_url', return_value=False)
    ret = gin_link_html()
    assert ret == '<a style="color: #fff; font-size: 15px; "href="https://test.github-domain/test_user/test_repo.git" target="_blank" rel="noopener"><button style="width: 300px; height: 30px; border-radius: 5px; background-color: #2185d0; border: 0px none;">GIN-forkに遷移する</button></a>'

    # リモートURLの更新失敗
    mocker.patch('nb_libs.utils.gin.sync.update_repo_url', side_effect=UnitTestError())
    ret = gin_link_html()
    assert ret == '<a style="color: #fff; font-size: 15px; "href="https://test.github-domain/test_user/test_repo.git" target="_blank" rel="noopener"><button style="width: 300px; height: 30px; border-radius: 5px; background-color: #2185d0; border: 0px none;">GIN-forkに遷移する</button></a>'
