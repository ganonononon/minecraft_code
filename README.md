# Minecraft Discord Bot

DiscordからMinecraftサーバー（AWS EC2）を操作できるBotです。

## 機能概要

- サーバーの起動・停止・状態確認
- ホワイトリスト管理（プレイヤーの追加・削除・一覧）
- プレイヤーの死亡をDiscordに通知

## ファイル構成

```
minecraft_code/
├── main.py            # Botのエントリーポイント（起動ファイル）
├── bot.py             # 旧バージョンのBot（Cog分割前）
├── log_monitor.py     # EC2側で動くログ監視スクリプト
└── cogs/              # 機能ごとに分割したモジュール
    ├── server.py      # サーバー操作（起動・停止・状態確認）
    ├── whitelist.py   # ホワイトリスト管理
    └── death.py       # 死亡通知の受信・Discord転送
```

---

## 各ファイルの説明

### `main.py` — Botの起動ファイル

Botを起動するメインスクリプト。`cogs/` 内のモジュールを読み込んで動かします。

- `cogs.server`（サーバー操作）を読み込む
- `cogs.whitelist`（ホワイトリスト管理）を読み込む

**起動方法:**
```bash
python main.py
```

---

### `cogs/server.py` — サーバー操作

AWS API Gateway経由でEC2インスタンスを操作するコマンド群。

| コマンド | 説明 |
|----------|------|
| `!panel` | 起動・停止・状態確認ボタンのパネルを表示 |
| `!start` | サーバーを起動 |
| `!stop` | サーバーを停止 |
| `!status` | サーバーの状態を確認 |

ボタン操作にも対応しており、`!panel` で表示されるボタンをクリックしても同様の操作ができます。

---

### `cogs/whitelist.py` — ホワイトリスト管理

MinecraftサーバーのホワイトリストをDiscordから操作するコマンド群。

| コマンド | 説明 |
|----------|------|
| `!whitelist add <プレイヤー名>` | ホワイトリストにプレイヤーを追加 |
| `!whitelist remove <プレイヤー名>` | ホワイトリストからプレイヤーを削除 |
| `!whitelist list` | 現在のホワイトリスト一覧を表示 |

---

### `cogs/death.py` — 死亡通知（Webhookサーバー）

`log_monitor.py` からの死亡通知を受け取り、Discordチャンネルに転送します。

- ポート `8080`（デフォルト）でHTTPサーバーを起動
- `POST /death` でEC2から死亡イベントを受信
- 指定したDiscordチャンネルにEmbedで通知を送信
- `X-Secret` ヘッダーによる簡易認証に対応

---

### `log_monitor.py` — ログ監視スクリプト（EC2側で動かす）

MinecraftサーバーのログファイルをリアルタイムWatchして、死亡メッセージを検出するスクリプト。

- `latest.log` を末尾から監視（起動前のログは無視）
- 死亡キーワード（`was slain by`, `drowned`, `fell from` など）を検出
- 検出時にDiscord WebhookへEmbedで通知を送信

**EC2での起動方法:**
```bash
python log_monitor.py
```

---

### `bot.py` — 旧バージョンのBot

Cog分割前のすべての機能が1ファイルにまとまったバージョンです。現在は `main.py` + `cogs/` に移行済みのため、参考用として残してあります。

---

## 環境変数

`.env` ファイルまたはシステムの環境変数に設定してください。

| 変数名 | 説明 | 使用ファイル |
|--------|------|-------------|
| `DISCORD_TOKEN` | DiscordボットのAPIトークン | `main.py`, `bot.py` |
| `API_GATEWAY_URL` | サーバー操作用のAWS API Gateway URL | `cogs/server.py`, `bot.py` |
| `WHITELIST_API_URL` | ホワイトリスト操作用のAWS API Gateway URL | `cogs/whitelist.py`, `bot.py` |
| `DEATH_CHANNEL_ID` | 死亡通知を送るDiscordチャンネルID | `cogs/death.py` |
| `DEATH_WEBHOOK_PORT` | 死亡通知受信ポート（デフォルト: 8080） | `cogs/death.py` |
| `DEATH_WEBHOOK_SECRET` | Webhook認証用シークレット（任意） | `cogs/death.py` |
| `MC_LOG_FILE` | MinecraftのログファイルパスEC2側 | `log_monitor.py` |
| `DISCORD_WEBHOOK_URL` | 死亡通知送信先のDiscord Webhook URL | `log_monitor.py` |
