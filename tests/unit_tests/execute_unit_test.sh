# 仮想環境作成
python3 -m venv test_env
. test_env/bin/activate

# パッケージインストール
python3 -m pip install --upgrade pip
pip3 install -r requirements_test.txt

# テスト実行
pytest tests/unit_tests -v --cov=nb_libs --cov-report=html --junitxml=coverage.xml

# カバレッジをzip化
zip htmlcov -r htmlcov
