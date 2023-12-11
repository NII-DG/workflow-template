# 仮想環境作成
python3 -m venv test_env
. test_env/bin/activate

# パッケージインストール
python3 -m pip install --upgrade pip
pip3 install -r requirements_test.txt

# ブラウザインストール
playwright install
playwright install msedge
playwright install chrome
playwright install-deps
python3 -m playwright install

# テスト実行
pytest -v tests/integration_tests --junitxml=coverage.xml ${@:1}

# スクリーンショットをzip化
zip screenshot -r screenshot
