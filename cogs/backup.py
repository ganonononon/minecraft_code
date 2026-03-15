# cogs/backup.py
import discord
from discord.ext import commands
from discord import app_commands
import boto3
from datetime import datetime
import os

class BackupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ec2 = boto3.client('ec2', region_name=os.getenv('AWS_REGION', 'ap-northeast-1'))
        self.volume_id = os.getenv('EBS_VOLUME_ID')  # .envで管理

    @app_commands.command(name="backup", description="EBSスナップショットを手動で作成します")
    @app_commands.checks.has_role("Admin")  # ロール制限推奨
    async def backup(self, interaction: discord.Interaction):
        # 即座にDefer（スナップショットは非同期なので）
        await interaction.response.defer(ephemeral=False)

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        embed = discord.Embed(
            title="📸 バックアップ開始",
            description=f"EBSスナップショットを作成中...",
            color=discord.Color.yellow()
        )
        embed.add_field(name="Volume ID", value=self.volume_id)
        embed.add_field(name="開始時刻", value=now)
        await interaction.followup.send(embed=embed)

        try:
            response = self.ec2.create_snapshot(
                VolumeId=self.volume_id,
                Description=f"Manual backup via Discord - {now}",
                TagSpecifications=[{
                    'ResourceType': 'snapshot',
                    'Tags': [
                        {'Key': 'Name', 'Value': f'minecraft-manual-{now}'},
                        {'Key': 'Type', 'Value': 'manual'},
                        {'Key': 'CreatedBy', 'Value': str(interaction.user)}
                    ]
                }]
            )
            snapshot_id = response['SnapshotId']

            embed = discord.Embed(
                title="✅ バックアップ開始完了",
                description="スナップショットの作成を開始しました。完了まで数分かかります。",
                color=discord.Color.green()
            )
            embed.add_field(name="Snapshot ID", value=snapshot_id, inline=False)
            embed.add_field(name="実行者", value=str(interaction.user))
            await interaction.followup.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="❌ バックアップ失敗",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BackupCog(bot))