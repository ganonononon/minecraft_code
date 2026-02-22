import discord
from discord.ext import commands
from discord.ui import Button, View
import requests
import json
import os
from dotenv import load_dotenv

# ========== 設定 ==========
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
API_GATEWAY_URL = os.getenv('API_GATEWAY_URL')
WHITELIST_API_URL = os.getenv('WHITELIST_API_URL')

# Bot設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ========== ホワイトリストコマンド ==========
@bot.group(name='whitelist', help='ホワイトリスト管理')
async def whitelist(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('使い方: `!whitelist add/remove/list <プレイヤー名>`')

@whitelist.command(name='add', help='ホワイトリストに追加')
async def whitelist_add(ctx, player: str):
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
async def whitelist_remove(ctx, player: str):
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
async def whitelist_list(ctx):
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

# ========== ボタンクラス ==========
class MinecraftControlView(View):
    def __init__(self):
        super().__init__(timeout=None)  # タイムアウトなし（常に有効）
    
    @discord.ui.button(label='🟢 起動', style=discord.ButtonStyle.success, custom_id='start_button')
    async def start_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        
        try:
            response = requests.post(
                API_GATEWAY_URL,
                json={'action': 'start'},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                await interaction.followup.send('✅ 起動リクエストを送信しました！', ephemeral=True)
            else:
                await interaction.followup.send(f'❌ エラー（ステータス: {response.status_code}）', ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f'❌ エラー: {str(e)}', ephemeral=True)
    
    @discord.ui.button(label='🔴 停止', style=discord.ButtonStyle.danger, custom_id='stop_button')
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        
        try:
            response = requests.post(
                API_GATEWAY_URL,
                json={'action': 'stop'},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                await interaction.followup.send('✅ 停止リクエストを送信しました！', ephemeral=True)
            else:
                await interaction.followup.send(f'❌ エラー（ステータス: {response.status_code}）', ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f'❌ エラー: {str(e)}', ephemeral=True)
    
    @discord.ui.button(label='📊 状態確認', style=discord.ButtonStyle.primary, custom_id='status_button')
    async def status_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        
        try:
            response = requests.post(
                API_GATEWAY_URL,
                json={'action': 'status'},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                await interaction.followup.send('✅ 確認完了！（詳細はチャンネルに通知されます）', ephemeral=True)
            else:
                await interaction.followup.send(f'❌ エラー（ステータス: {response.status_code}）', ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f'❌ エラー: {str(e)}', ephemeral=True)

# ========== イベント ==========
@bot.event
async def on_ready():
    print(f'{bot.user} でログインしました！')
    print(f'Bot ID: {bot.user.id}')
    print('------')
    
    # 既存のViewを再登録（bot再起動時にボタンが動くようにする）
    bot.add_view(MinecraftControlView())

# ========== コマンド ==========
@bot.command(name='panel')
async def show_panel(ctx):
    """操作パネルを表示"""
    embed = discord.Embed(
        title="🎮 マインクラフトサーバー管理",
        description="ボタンをクリックしてサーバーを操作できます",
        color=discord.Color.blue()
    )
    
    view = MinecraftControlView()
    await ctx.send(embed=embed, view=view)

# 従来のコマンドも残す（オプション）
@bot.command(name='start')
async def start_server(ctx):
    """マインクラフトサーバーを起動"""
    await ctx.send('⏳ サーバーを起動しています...')
    
    try:
        response = requests.post(
            API_GATEWAY_URL,
            json={'action': 'start'},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            await ctx.send('✅ 起動リクエストを送信しました！')
        else:
            await ctx.send(f'❌ エラー（ステータス: {response.status_code}）')
    except Exception as e:
        await ctx.send(f'❌ エラー: {str(e)}')

@bot.command(name='stop')
async def stop_server(ctx):
    """マインクラフトサーバーを停止"""
    await ctx.send('⏳ サーバーを停止しています...')
    
    try:
        response = requests.post(
            API_GATEWAY_URL,
            json={'action': 'stop'},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            await ctx.send('✅ 停止リクエストを送信しました！')
        else:
            await ctx.send(f'❌ エラー（ステータス: {response.status_code}）')
    except Exception as e:
        await ctx.send(f'❌ エラー: {str(e)}')

@bot.command(name='status')
async def server_status(ctx):
    """サーバーの状態とIPアドレスを確認"""
    await ctx.send('⏳ サーバー状態を確認中...')
    
    try:
        response = requests.post(
            API_GATEWAY_URL,
            json={'action': 'status'},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            await ctx.send('✅ 確認完了！（詳細はWebhook通知で届きます）')
        else:
            await ctx.send(f'❌ エラー（ステータス: {response.status_code}）')
    except Exception as e:
        await ctx.send(f'❌ エラー: {str(e)}')

# ========== Bot起動 ==========
if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
