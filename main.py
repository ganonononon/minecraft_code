import discord
from discord.ext import commands
import os

# ========== 設定 ==========
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Bot設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ========== イベント ==========
@bot.event
async def on_ready():
    print(f'{bot.user} でログインしました！')
    print(f'Bot ID: {bot.user.id}')
    guild_id = int(os.getenv('GUILD_ID', '0'))
    if guild_id:
        guild = discord.Object(id=guild_id)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print(f'スラッシュコマンドをSyncしました（ギルド: {guild_id}）')
    else:
        await bot.tree.sync()
        print('スラッシュコマンドをSyncしました（グローバル）')
    print('------')

# ========== Cog読み込み ==========
async def main():
    async with bot:
        await bot.load_extension('cogs.server')
        await bot.load_extension('cogs.whitelist')
        await bot.load_extension('cogs.backup')
        await bot.load_extension('cogs.death')
        await bot.start(DISCORD_TOKEN)

# ========== Bot起動 ==========
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
