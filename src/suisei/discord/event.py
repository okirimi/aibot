from discord import app_commands

from src.suisei.discord.client import BotClient

_client: BotClient = BotClient.get_instance()

# 別のハンドラーも追加予定

# 後の利用可能性のために残しておく
_ERROR_MESSAGES = {
    app_commands.CheckFailure: "**CheckFailure** - コマンドの実行条件を満たしていません",
    app_commands.CommandInvokeError: (
        "**CommandInvokeError** - コマンドの実行中にエラーが発生しました"
    ),
    app_commands.CommandSignatureMismatch: (
        "**CommandSignatureMismatch** - コマンドの引数が正しくありません"
    ),
    app_commands.CommandNotFound: "**CommandNotFound** - コマンドが見つかりません",
    app_commands.MissingRole: "**MissingRole** - 必要なロールがありません",
    app_commands.MissingAnyRole: ("**MissingAnyRole** - いずれかの必要なロールがありません"),
    app_commands.MissingPermissions: "**MissingPermissions** - コマンドの実行権限がありません",
    app_commands.BotMissingPermissions: (
        "**BotMissingPermissions** - ボットに必要な権限がありません"
    ),
    app_commands.TransformerError: "**TransformerError** - 引数の変換に失敗しました",
}
