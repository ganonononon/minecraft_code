# Minecraft Discord Bot

DiscordからMinecraftサーバー（AWS EC2）を操作できるBotです。

---

## 機能一覧

| 機能 | コマンド | 説明 |
|------|----------|------|
| サーバー操作パネル | `!panel` | 起動・停止・状態確認ボタンのパネルを表示 |
| サーバー起動 | `!start` | Minecraftサーバーを起動する |
| サーバー停止 | `!stop` | Minecraftサーバーを停止する |
| 状態確認 | `!status` | サーバーの状態を確認する |
| ホワイトリスト追加 | `!whitelist add <名前>` | プレイヤーをホワイトリストに追加 |
| ホワイトリスト削除 | `!whitelist remove <名前>` | プレイヤーをホワイトリストから削除 |
| ホワイトリスト一覧 | `!whitelist list` | 現在のホワイトリストを表示 |
| バックアップ | `/backup` | EBSスナップショットを手動で作成 |
| 死亡通知 | 自動 | プレイヤーの死亡をDiscordチャンネルに通知 |

---

## 各機能の説明

### サーバー操作（`cogs/server.py`）

AWS API Gateway 経由で EC2 インスタンスを操作します。
`!panel` コマンドでボタンパネルを表示すると、クリックだけで操作できます。

### ホワイトリスト管理（`cogs/whitelist.py`）

Minecraftサーバーへの参加を許可するプレイヤーをDiscordから管理できます。

### EBSバックアップ（`cogs/backup.py`）

`/backup` コマンドで AWS EBS のスナップショットを即座に作成します。
サーバーの起動・停止に関わらず実行でき、作成された Snapshot ID を Discord に通知します。

### 死亡通知（`cogs/death.py`）

Bot がバックグラウンドで Minecraft のログファイルを1秒ごとに監視し、
プレイヤーの死亡を検出すると指定した Discord チャンネルに自動通知します。
別スクリプトの起動は不要で、Bot 起動だけで動作します。

---

## ファイル構成

```
minecraft_code/
├── main.py              # Botのエントリーポイント
├── requirements.txt     # 必要なPythonライブラリ一覧
├── .env                 # 環境変数（GitHubには上げない）
├── .env.example         # 環境変数のテンプレート
├── log_monitor.py       # 旧ログ監視スクリプト（death.pyに統合済み）
├── bot.py               # 旧バージョンのBot（参考用）
└── cogs/
    ├── server.py        # サーバー操作
    ├── whitelist.py     # ホワイトリスト管理
    ├── backup.py        # EBSバックアップ
    └── death.py         # 死亡通知（ログ監視込み）
```

---

## セットアップ

### 1. 環境変数の設定

`.env.example` をコピーして `.env` を作成し、各値を入力してください。

```bash
cp .env.example .env
```

### 2. ライブラリのインストール

```bash
pip3 install -r requirements.txt
```

### 3. Bot の起動

```bash
# 通常起動（ターミナルを閉じると停止）
python3 main.py

# バックグラウンド起動（SSHを切っても動き続ける）
nohup python3 main.py > bot.log 2>&1 &
```

---

## 環境変数一覧

| 変数名 | 説明 | 必須/任意 |
|--------|------|----------|
| `DISCORD_TOKEN` | DiscordボットのAPIトークン | 必須 |
| `GUILD_ID` | DiscordサーバーのID | 必須 |
| `API_GATEWAY_URL` | サーバー操作用のAPI Gateway URL | 必須 |
| `WHITELIST_API_URL` | ホワイトリスト操作用のAPI Gateway URL | 必須 |
| `EBS_VOLUME_ID` | バックアップ対象のEBSボリュームID | 必須 |
| `DEATH_CHANNEL_ID` | 死亡通知を送るDiscordチャンネルID | 必須 |
| `AWS_REGION` | AWSリージョン（デフォルト: `ap-northeast-1`） | 任意 |
| `MC_LOG_FILE` | Minecraftのログファイルパス（デフォルト: `/home/ubuntu/minecraft_server/logs/latest.log`） | 任意 |

---

## デプロイ

`main` ブランチに push すると GitHub Actions が自動で EC2 にデプロイし、Bot を再起動します。

必要な GitHub Secrets：

| シークレット名 | 内容 |
|---------------|------|
| `EC2_HOST` | EC2のIPアドレス |
| `EC2_USER` | SSHユーザー名（通常 `ubuntu`） |
| `EC2_SSH_KEY` | SSH秘密鍵 |
