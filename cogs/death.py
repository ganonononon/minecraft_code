import discord
from discord.ext import commands, tasks
import asyncio
import os
import re

# ========== 設定 ==========
DEATH_CHANNEL_ID = int(os.getenv('DEATH_CHANNEL_ID', '0'))
MC_LOG_FILE = os.getenv('MC_LOG_FILE', '/home/ubuntu/minecraft_server/logs/latest.log')

# ========== 死亡メッセージのパターン ==========
LOG_LINE_PATTERN = re.compile(r'\[Server thread/INFO\]: (.+)')

DEATH_KEYWORDS = [
    'was slain by',
    'was shot by',
    'was blown up by',
    'was killed by',
    'drowned',
    'fell from',
    'fell off',
    'hit the ground',
    'burned to death',
    'tried to swim in lava',
    'suffocated',
    'blew up',
    'starved to death',
    'died',
    'was impaled',
    'experienced kinetic energy',
    'was pummeled',
    'went up in flames',
]


def is_death_message(message: str) -> bool:
    return any(keyword in message for keyword in DEATH_KEYWORDS)


# ========== 死亡通知Cog ==========
class DeathCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._log_file = None
        self.monitor_log.start()

    async def cog_unload(self):
        self.monitor_log.cancel()
        if self._log_file:
            self._log_file.close()

    @tasks.loop(seconds=1)
    async def monitor_log(self):
        """ログファイルを1秒ごとに確認して死亡メッセージを検出する"""
        if self._log_file is None:
            return
        while True:
            line = self._log_file.readline()
            if not line:
                break
            match = LOG_LINE_PATTERN.search(line)
            if not match:
                continue
            message = match.group(1)
            if is_death_message(message):
                player = message.split()[0] if message else 'Unknown'
                await self.send_death_notification(player, message)

    @monitor_log.before_loop
    async def before_monitor_log(self):
        """Bot起動完了を待ってからログファイルを開く"""
        await self.bot.wait_until_ready()
        try:
            self._log_file = open(MC_LOG_FILE, 'r', encoding='utf-8')
            self._log_file.seek(0, 2)  # ファイル末尾から監視開始
            print(f'ログ監視開始: {MC_LOG_FILE}')
        except FileNotFoundError:
            print(f'警告: ログファイルが見つかりません: {MC_LOG_FILE}')

    async def send_death_notification(self, player: str, message: str):
        """Discordチャンネルに死亡通知を送る"""
        channel = self.bot.get_channel(DEATH_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title='💀 プレイヤーが死亡しました',
                description=f'**{message}**',
                color=discord.Color.red()
            )
            embed.set_footer(text=f'Player: {player}')
            await channel.send(embed=embed)
        else:
            print(f'エラー: チャンネルID {DEATH_CHANNEL_ID} が見つかりません')


async def setup(bot):
    await bot.add_cog(DeathCog(bot))
