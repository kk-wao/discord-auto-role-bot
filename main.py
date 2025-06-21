import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive
from flask import request  # keep_alive.pyで必要
import sys
import datetime

import sys
import os
import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

class DateRotatingLogger:
    def __init__(self, is_error=False):
        self.is_error = is_error
        self.current_date = datetime.date.today()
        self.log_file = self._open_log_file()

    def _get_filename(self):
        date_str = self.current_date.strftime("%Y-%m-%d")
        kind = "error" if self.is_error else "log"
        return os.path.join(LOG_DIR, f"{kind}_{date_str}.txt")

    def _open_log_file(self):
        return open(self._get_filename(), "a", encoding="utf-8")

    def write(self, message):
        today = datetime.date.today()
        if today != self.current_date:
            self.log_file.close()
            self.current_date = today
            self.log_file = self._open_log_file()

        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
        if message.strip():
            self.log_file.write(timestamp + message)
            self.log_file.flush()

        target = sys.__stderr__ if self.is_error else sys.__stdout__
        target.write(message)
        target.flush()

    def flush(self):
        self.log_file.flush()

# stdout と stderr にセット
sys.stdout = DateRotatingLogger(is_error=False)
sys.stderr = DateRotatingLogger(is_error=True)


# 環境変数読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ROLE_ID = int(os.getenv("ROLE_ID"))

# ログ
print("Bot starting...")
print("TOKEN is set:", bool(TOKEN))
print("CHANNEL_ID is set:", bool(CHANNEL_ID))
print("ROLE_ID is set:", bool(ROLE_ID))

# Discordの意図を全て取得
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == CHANNEL_ID:
        guild = message.guild
        member = message.author
        role = guild.get_role(ROLE_ID)

        if role and role not in member.roles:
            try:
                await member.add_roles(role)
                print(f"{member.name} にロール「{role.name}」を付与しました。")
            except discord.Forbidden:
                print("ロールを付与する権限がありません。")
            except Exception as e:
                print(f"エラー: {e}")

    await bot.process_commands(message)

# 非同期でBot起動を管理する関数
async def run_bot():
    retry_delay = 300  # 秒（5分）
    max_error_count = 3  # 最大許容連続エラー回数
    error_count = 0

    while True:
        try:
            await bot.start(TOKEN)
            error_count = 0  # 成功したらカウントリセット
        except discord.errors.HTTPException as e:
            if e.status == 429:
                print("レートリミットに達しました。5分待機して再接続します。")
                await asyncio.sleep(retry_delay)
            else:
                print(f"HTTPエラー: {e}")
                error_count += 1
                print(f"{retry_delay}秒後に再接続します。エラーカウント: {error_count}")
                await asyncio.sleep(retry_delay)
        except Exception as e:
            print(f"その他のエラー: {e}")
            error_count += 1
            print(f"{retry_delay}秒後に再接続します。エラーカウント: {error_count}")
            await asyncio.sleep(retry_delay)

        if error_count >= max_error_count:
            print("エラーが連続で発生しました。Replitを強制再起動します。")
            os._exit(1)  # Replit環境ではこれでプロセスが再起動される

# Flaskサーバー（Replit用）を起動
keep_alive()

# 非同期イベントループでBotを実行
if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except Exception as e:
        print(f"メインループ例外: {e}")
        import time
        time.sleep(10)  # watchdog が拾うまで少し時間を与える
        os._exit(1)

