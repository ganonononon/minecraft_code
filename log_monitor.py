"""
Minecraftサーバー(EC2)側で動かすログ監視スクリプト。
死亡メッセージを検出してDiscord Webhookに直接通知を送る。

使い方:
  python log_monitor.py

環境変数:
  MC_LOG_FILE          - Minecraftのログファイルパス
  DISCORD_WEBHOOK_URL  - DiscordのWebhook URL
"""

import re
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ========== 設定 ==========
LOG_FILE = os.getenv('MC_LOG_FILE', '/home/ubuntu/minecraft_server/logs/latest.log')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')

# ========== 死亡メッセージのパターン ==========
# Minecraftログの形式: [HH:MM:SS] [Server thread/INFO]: メッセージ
LOG_LINE_PATTERN = re.compile(r'\[Server thread/INFO\]: (.+)')

# 死亡メッセージに含まれるキーワード一覧
DEATH_KEYWORDS = [
    'was slain by',           # ～に倒された
    'was shot by',            # ～に射られた
    'was blown up by',        # ～に吹き飛ばされた
    'was killed by',          # ～に殺された
    'drowned',                # 溺死
    'fell from',              # 落下死
    'fell off',               # 落下死
    'hit the ground',         # 落下死
    'burned to death',        # 焼死
    'tried to swim in lava',  # 溶岩死
    'suffocated',             # 窒息死
    'blew up',                # 爆死
    'starved to death',       # 飢え死
    'died',                   # その他の死
    'was impaled',            # 突き刺された
    'experienced kinetic energy',  # 壁激突死
    'was pummeled',           # 殴り殺された
    'went up in flames',      # 炎上死
]


def is_death_message(message: str) -> bool:
    """メッセージが死亡メッセージかどうか判定する"""
    return any(keyword in message for keyword in DEATH_KEYWORDS)


def extract_player_name(message: str) -> str:
    """死亡メッセージからプレイヤー名を取り出す（最初の単語）"""
    return message.split()[0] if message else 'Unknown'


def send_death_notification(player: str, message: str):
    """Discord Webhookに死亡通知を送る"""
    # Discord Embedの形式で送信（赤色: 0xFF0000 = 16711680）
    payload = {
        'embeds': [{
            'title': '💀 プレイヤーが死亡しました',
            'description': f'**{message}**',
            'color': 16711680,
            'footer': {'text': f'Player: {player}'}
        }]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code == 204:  # Discordは成功時に204を返す
            print(f'通知送信成功: {message}')
        else:
            print(f'通知送信失敗 (ステータス: {response.status_code}): {message}')
    except Exception as e:
        print(f'通知送信エラー: {e}')


def monitor_log():
    """ログファイルを監視して死亡メッセージを検出する"""
    if not DISCORD_WEBHOOK_URL:
        print('エラー: DISCORD_WEBHOOK_URL が設定されていません')
        return

    print(f'ログ監視開始: {LOG_FILE}')

    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        # ファイルの末尾から監視開始（過去のログは無視）
        f.seek(0, 2)

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)  # 新しい行が来るまで待つ
                continue

            # ログ行からメッセージ部分を取り出す
            match = LOG_LINE_PATTERN.search(line)
            if not match:
                continue

            message = match.group(1)

            # 死亡メッセージなら通知を送る
            if is_death_message(message):
                player = extract_player_name(message)
                print(f'死亡検出: {message}')
                send_death_notification(player, message)


if __name__ == '__main__':
    monitor_log()
