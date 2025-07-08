# AiBot

![Python](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white&style=flat&labelColor=24292e)
![License](https://img.shields.io/badge/License-BSD--3--Clause-orange.svg?style=flat&labelColor=24292e)

**AiBot**は、あなただけのキャラクターを設定し、会話を行ったり文章やコードの修正などの作業をサポートするDiscord Botです。

## Features

以下に機能ごとのスラッシュコマンドを紹介します。

> [!IMPORTANT]
> 管理者権限が必要とされるスラッシュコマンドは、環境変数 `ADMIN_USER_IDS` に登録されたユーザーIDを持つユーザーのみが実行可能です。
> 権限のないユーザーがこれらを実行した場合、エラーメッセージが当該ユーザーのUIに表示されますが、アプリの動作には影響しません。

<table>
  <thead>
    <tr>
      <th>カテゴリ</th>
      <th>コマンド</th>
      <th>説明</th>
      <th>権限</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="1">グローバル設定</td>
      <td><code>/provider</code></td>
      <td>利用するAIプロバイダーの選択</td>
      <td>管理者</td>
    </tr>
    <tr>
      <td rowspan="7">チャット機能</td>
      <td><code>/chat</code></td>
      <td>AIとシングルターンの会話を行う</td>
      <td>-</td>
    </tr>
    <tr>
      <td><code>/system</code></td>
      <td>システムプロンプトを設定</td>
      <td>-</td>
    </tr>
    <tr>
      <td><code>/systemlist</code></td>
      <td>以前のシステムプロンプトを検索し、内容を閲覧</td>
      <td>-</td>
    </tr>
    <tr>
      <td><code>/reuse</code></td>
      <td>以前のシステムプロンプトを現在の設定として反映</td>
      <td>-</td>
    </tr>
    <tr>
      <td><code>/resetsystem</code></td>
      <td>システム指示をデフォルトにリセット（強制システムモード中は無効）</td>
      <td>-</td>
    </tr>
    <tr>
      <td><code>/forcesystem</code></td>
      <td>デフォルトのシステム指示を強制的に適用</td>
      <td>管理者</td>
    </tr>
    <tr>
      <td><code>/unlocksystem</code></td>
      <td>強制システムモードを解除</td>
      <td>管理者</td>
    </tr>
    <tr>
      <td rowspan="1">コード修正</td>
      <td><code>/fixpy</code></td>
      <td>Pythonコードのバグ検出と修正</td>
      <td>-</td>
    </tr>
    <tr>
      <td rowspan="3">アクセス制御</td>
      <td><code>/grant</code></td>
      <td>ユーザーへのアクセス権限付与</td>
      <td>管理者</td>
    </tr>
    <tr>
      <td><code>/revoke</code></td>
      <td>ユーザーのアクセス権限取り消し</td>
      <td>管理者</td>
    </tr>
    <tr>
      <td><code>/check</code></td>
      <td>ユーザーのアクセス権限確認</td>
      <td>管理者</td>
    </tr>
  </tbody>
</table>

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

最後に、`.env` と `.resources/system_instructions.yml` の内容が正しいことを確認してから、botを起動してください。

```bash
python -m src.aibot --log <log_level>
```

> [!TIP]
> `--log <log_level>` パラメータは任意で、ログレベルを設定できます。使用可能な値は `DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`（大文字小文字は区別されません）です。
> 指定しない場合、デフォルトで `INFO` が使用されます。

## References

- https://github.com/openai/gpt-discord-bot
