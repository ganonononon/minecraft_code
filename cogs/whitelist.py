from discord.ext import commands
import requests
import json
import os

WHITELIST_API_URL = os.getenv('WHITELIST_API_URL')

# ========== ホワイトリストCog ==========
class WhitelistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='whitelist', help='ホワイトリスト管理')
    async def whitelist(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('使い方: `!whitelist add/remove/list <プレイヤー名>`')

    @whitelist.command(name='add', help='ホワイトリストに追加')
    async def whitelist_add(self, ctx, player: str):
        await ctx.send(f'⏳ {player} を追加中...')
        try:
            response = requests.post(
                WHITELIST_API_URL,
                json={'action': 'add', 'player': player},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                if 'body' in result and isinstance(result['body'], str):
                    body = json.loads(result['body'])
                    await ctx.send(body['message'])
                elif 'message' in result:
                    await ctx.send(result['message'])
                else:
                    await ctx.send(f'❌ レスポンス形式エラー: {result}')
            else:
                await ctx.send(f'❌ エラー（ステータス: {response.status_code}）')
        except Exception as e:
            await ctx.send(f'❌ エラー: {str(e)}')

    @whitelist.command(name='remove', help='ホワイトリストから削除')
    async def whitelist_remove(self, ctx, player: str):
        await ctx.send(f'⏳ {player} を削除中...')
        try:
            response = requests.post(
                WHITELIST_API_URL,
                json={'action': 'remove', 'player': player},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                if 'body' in result and isinstance(result['body'], str):
                    body = json.loads(result['body'])
                    await ctx.send(body['message'])
                elif 'message' in result:
                    await ctx.send(result['message'])
                else:
                    await ctx.send(f'❌ レスポンス形式エラー: {result}')
            else:
                await ctx.send(f'❌ エラー（ステータス: {response.status_code}）')
        except Exception as e:
            await ctx.send(f'❌ エラー: {str(e)}')

    @whitelist.command(name='list', help='ホワイトリスト一覧')
    async def whitelist_list(self, ctx):
        await ctx.send('⏳ ホワイトリストを確認中...')
        try:
            response = requests.post(
                WHITELIST_API_URL,
                json={'action': 'list'},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                if 'body' in result and isinstance(result['body'], str):
                    body = json.loads(result['body'])
                    await ctx.send(body['message'])
                elif 'message' in result:
                    await ctx.send(result['message'])
                else:
                    await ctx.send(f'❌ レスポンス形式エラー: {result}')
            else:
                await ctx.send(f'❌ エラー（ステータス: {response.status_code}）')
        except Exception as e:
            await ctx.send(f'❌ エラー: {str(e)}')


async def setup(bot):
    await bot.add_cog(WhitelistCog(bot))
