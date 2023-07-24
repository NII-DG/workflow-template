import panel as pn
from IPython.display import clear_output, display, HTML


def dg_menu(type='research'):
    pn.extension()

    menu_option = {}

    menu_option['--'] = 1

    if type == 'research':
        menu_option['研究リポジトリ名を確認する'] = 2
        menu_option['研究フロートップページへの遷移する'] = 3

    elif type == 'experiment':
        menu_option['研究リポジトリ名・実験パッケージ名を確認する'] = 4
        menu_option['実験フロートップページへの遷移する'] = 5

    menu_option['GIN-forkへ遷移する'] = 6

    # プルダウン形式のセレクターを生成
    menu_selector = pn.widgets.Select(name='メニューの選択', options=menu_option, value=1)

    html_output  = pn.pane.HTML()

    def update_selected_value(event):
        selected_value = event.new

        if selected_value == 1:
            html_output.object = ''
        elif selected_value == 2:
            url = 'https://www.yahoo.co.jp/'
            msg = 'yahoo'
            target='_blank'
            html_output.object = f'<a href="{url}" target="{target}" ><button>{msg}</button></a>'
        elif selected_value == 3:
            pass
        elif selected_value == 4:
            pass
        elif selected_value == 5:
            pass
        elif selected_value == 6:
            url = 'https://www.google.com/'
            msg = 'google'
            target='_blank'
            html_output.object = f'<a href="{url}" target="{target}" ><button>{msg}</button></a>'

    menu_selector.param.watch(update_selected_value,'value')
    display(menu_selector)
    display(html_output)
