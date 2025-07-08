# AiBot

![Python](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white&style=flat&labelColor=24292e)
![License](https://img.shields.io/badge/License-BSD--3--Clause-orange.svg?style=flat&labelColor=24292e)

**AiBot**は、AIにあなただけのキャラクターを設定し、会話を行ったり文章やコードの修正などの作業をサポートするDiscord Botです。

## Features

以下に機能ごとのスラッシュコマンドを紹介します。

> [!IMPORTANT]
> 管理者権限が必要とされるスラッシュコマンド（`/provider`, `/grant`, `/revoke`, `/check`）は、環境変数 `ADMIN_USER_IDS` に登録されたユーザーIDを持つユーザーのみが実行可能です。
> 権限のないユーザーがこれらを実行した場合、エラーメッセージが当該ユーザーのUIに表示されますが、アプリの動作には影響しません。

### グローバル設定
- `/provider`: 利用するAIプロバイダーの選択（管理者のみ）

### チャット機能
- `/chat`: AIとシングルターンの会話を行います
- `/system`: システムプロンプトを設定します
- `/systemlist`: 以前のシステムプロンプトを検索し、内容を閲覧できます
- `/reuse`: 以前のシステムプロンプトを現在の設定として反映します
- `/resetsystem`: システム指示をデフォルトにリセットします（強制システムモード中は無効）
- `/forcesystem`: デフォルトのシステム指示を強制的に適用します（管理者のみ）
- `/unlocksystem`: 強制システムモードを解除します（管理者のみ）

### コード修正
- `/fixpy`: Pythonコードのバグ検出と修正

### アクセス制御
- `/grant`: ユーザーへのアクセス権限付与（管理者のみ）
- `/revoke`: ユーザーのアクセス権限取り消し（管理者のみ）
- `/check`: ユーザーのアクセス権限確認（管理者のみ）

## Getting started

### Prerequisites

以下の準備が必要です:
- Python 3.12の実行環境
- Discord Bot Token
- Anthropic API キー（オプション）
- OpenAI API キー（オプション）
- Google Gemini API キー（オプション）

詳細な手順については、[PREREQUISITES.md](https://github.com/okirimi/aibot/blob/main/docs/PREREQUISITES.md)を参照してください。

### インストール手順

**1. リポジトリのクローンと依存関係のインストール**

```bash
# ----- リポジトリのクローン -----
git clone https://github.com/okirimi/aibot.git
cd aibot

# ----- 依存関係のインストール -----
# uvを使用する場合
uv sync

# uvを使用しない場合
pip install -r requirements.lock
```

**2. 環境設定ファイルの準備**

設定に`.env`ファイルを使用します。以下の手順に従ってください：
- `.emv.sample`のコピーを作成し、`.env`に改名
- `.env`に実際の値を入力

**3. システム指示の設定**

`resources/system_instructions.yml`にデフォルトのシステム指示を設定できます。

> [!IMPORTANT]
> 一般公開されているDiscordサーバーや、多くのユーザーが利用する場面では、システムプロンプトの設定を適切に行うことを強く推奨します。

**4. Botの起動**

最後に、`.env` ファイルと `.prompt.sample.yml` ファイルのすべての値が正しく入力されていることを確認し、次のコマンドを実行してください：

```bash
python -m src.aibot --log <ログレベル>
```

> [!TIP]
> `--log <log_level>` パラメータは任意で、ログレベルを設定できます。使用可能な値は `DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`（大文字小文字は区別されません）です。
> 指定しない場合、デフォルトで `INFO` が使用されます。

## References

- https://github.com/openai/gpt-discord-bot
