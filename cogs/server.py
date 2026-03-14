import discord
from discord.ext import commands
from discord.ui import Button, View
import requests
import os

API_GATEWAY_URL = os.getenv('API_GATEWAY_URL')

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


# ========== サーバー操作Cog ==========
class ServerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ボタンを再登録（bot再起動時にボタンが動くようにする）
        self.bot.add_view(MinecraftControlView())

    @commands.command(name='panel')
    async def show_panel(self, ctx):
        """操作パネルを表示"""
        embed = discord.Embed(
            title="🎮 マインクラフトサーバー管理",
            description="ボタンをクリックしてサーバーを操作できます",
            color=discord.Color.blue()
        )
        view = MinecraftControlView()
        await ctx.send(embed=embed, view=view)

    @commands.command(name='start')
    async def start_server(self, ctx):
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

    @commands.command(name='stop')
    async def stop_server(self, ctx):
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

    @commands.command(name='status')
    async def server_status(self, ctx):
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


async def setup(bot):
    await bot.add_cog(ServerCog(bot))
