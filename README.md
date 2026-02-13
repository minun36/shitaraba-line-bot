# したらば掲示板→Discord自動送信システム

毎日夜12時に、したらばVALORANT 2代目掲示板から最新スレッドを取得して指定したDiscordサーバーのチャンネルに通知します。

## 機能

- したらば掲示板から「VALORANT part～～～～」スレッドを自動取得
- レス数300以上の最新スレッドを選択
- 生成した全レスをUTF-8テキストファイルとして出力し、Discordにファイル添付で送信
- GitHub Actionsで完全自動実行（サーバー不要）

## セットアップ

### 1. Discord Bot トークン と チャンネルID を GitHub Secrets に登録

1. GitHubリポジトリの **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** をクリック
3. Name: `DISCORD_BOT_TOKEN`（値: Bot トークン）
4. Name: `DISCORD_CHANNEL_ID`（値: 送信先チャンネルID）
5. **Add secret** をクリック

※ トークンやチャンネルIDはリポジトリに直接置かず環境変数/Secretsのみで管理してください。

### 2. ローカルでの動作確認

ローカルで実行する場合は環境変数を設定してから実行してください。

Windows (PowerShell):
```powershell
$env:DISCORD_BOT_TOKEN = "あなたのボットトークン"
$env:DISCORD_CHANNEL_ID = "送信先チャンネルID"
python main.py
```

Linux / macOS:
```bash
export DISCORD_BOT_TOKEN="あなたのボットトークン"
export DISCORD_CHANNEL_ID="送信先チャンネルID"
python main.py
```

### 3. GitHub Actions での自動実行

`.github/workflows/daily_scrape.yml` が毎日 00:00 JST に実行する設定になっています。手動実行も可能です。

## カスタマイズ

### 送信形式の変更

本システムは全文をテキストファイルとして `outputs/` 配下に保存し、そのファイルをDiscordへ添付送信します。プレビュー件数ではなくファイル内容を編集してカスタマイズしてください。

### 実行時刻を変更

`.github/workflows/daily_scrape.yml` の `cron` を編集してください（UTC表記）。

## トラブルシューティング

### Discord に通知が来ない

- GitHub Secrets に `DISCORD_BOT_TOKEN` と `DISCORD_CHANNEL_ID` が正しく設定されているか確認
- Bot に該当チャンネルへの送信権限（Send Messages）があるか確認
- Actions タブでエラーログを確認

### スレッドが見つからない

- スレッド名のパターンを確認
- レス数の条件（300以上）を確認

## 依存関係

依存は `requirements.txt` を参照してください（`requests`, `beautifulsoup4`）。

## ライセンス

MIT License

