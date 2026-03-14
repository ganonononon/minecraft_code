import discord
from discord.ext import commands
from aiohttp import web
import asyncio
import os

# ========== 設定 ==========
DEATH_CHANNEL_ID = int(os.getenv('DEATH_CHANNEL_ID', '0'))  # 通知先チャンネルID
DEATH_WEBHOOK_PORT = int(os.getenv('DEATH_WEBHOOK_PORT', '8080'))  # 受信ポート
DEATH_WEBHOOK_SECRET = os.getenv('DEATH_WEBHOOK_SECRET', '')  # セキュリティ用シークレット

# ========== 死亡通知Cog ==========
class DeathCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self.app.router.add_post('/death', self.handle_death_event)
        self.runner = None

    async def cog_load(self):
        """Cog読み込み時にWebhookサーバーを起動"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, '0.0.0.0', DEATH_WEBHOOK_PORT)
        await site.start()
        print(f'死亡通知Webhookサーバー起動中 (ポート: {DEATH_WEBHOOK_PORT})')

    async def cog_unload(self):
        """Cog削除時にサーバーを停止"""
        if self.runner:
            await self.runner.cleanup()

    async def handle_death_event(self, request: web.Request) -> web.Response:
        """Minecraftサーバーからの死亡通知を受け取る"""
        # シークレットキーの確認（設定している場合）
        if DEATH_WEBHOOK_SECRET:
            secret = request.headers.get('X-Secret', '')
            if secret != DEATH_WEBHOOK_SECRET:
                return web.Response(status=403, text='Forbidden')

        try:
            data = await request.json()
        except Exception:
            return web.Response(status=400, text='Invalid JSON')

        player = data.get('player', 'Unknown')
        message = data.get('message', '死亡しました')

        # Discordチャンネルに通知を送る
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

        return web.Response(text='OK')


async def setup(bot):
    await bot.add_cog(DeathCog(bot))
