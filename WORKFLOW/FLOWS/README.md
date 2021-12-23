# FLOWS

## FLOWSでは分野ごとのフロー群を整理する

## ◆◆◆開発メモ◆◆◆

現時点では、プロトタイプを動かすために以下の作業が必要

- .gitconfigにユーザー名とメールアドレスを登録する
- jupyterhubでid_rsa（秘密鍵）を.ssh下に配置し、ginリポジトリにペアの公開鍵を登録する
- .gitignoreで.local以下のファイルをgit管理から外す
- .ssh/configで以下を指定
    host *
            StrictHostKeyChecking no
            UserKnownHostsFile=/dev/null


