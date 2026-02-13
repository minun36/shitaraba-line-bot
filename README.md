# したらば掲示板→LINE自動送信システム

毎日夜12時に、したらばVALORANT 2代目掲示板から最新スレッドを取得してLINEに通知します。

## 機能

- したらば掲示板から「VALORANT part～～～～」スレッドを自動取得
- レス数300以上の最新スレッドを選択
- 最初の20レスをLINEで通知
- GitHub Actionsで完全自動実行（サーバー不要）

## セットアップ

### 1. LINE Notify トークンを GitHub Secrets に登録

1. GitHubリポジトリの **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** をクリック
3. Name: `LINE_NOTIFY_TOKEN`
4. Secret: あなたのLINE Notifyトークン
5. **Add secret** をクリック

### 2. 動作確認（手動実行）

1. **Actions** タブを開く
2. 左側のワークフロー名をクリック
3. **Run workflow** → **Run workflow** で実行
4. 数分後、LINEに通知が届けばOK！

## 自動実行スケジュール

- **毎日 00:00 JST（夜12時）** に自動実行

## カスタマイズ

### 送信するレス数を変更

`main.py` の以下の部分を編集:

```python
preview_posts = posts[:20]  # ← 20を任意の数に変更
```

### 実行時刻を変更

`.github/workflows/daily_scrape.yml` の以下の部分を編集:

```yaml
cron: '0 15 * * *'  # 15:00 UTC = 00:00 JST
```

例: 朝9時に変更 → `cron: '0 0 * * *'`（00:00 UTC = 09:00 JST）

## トラブルシューティング

### LINEに通知が来ない

- GitHub Secrets に `LINE_NOTIFY_TOKEN` が正しく設定されているか確認
- Actions タブでエラーログを確認

### スレッドが見つからない

- スレッド名のパターンを確認
- レス数の条件（300以上）を確認

## ローカルでのテスト方法

```bash
# 依存ライブラリをインストール
pip install -r requirements.txt

# 環境変数を設定
export LINE_NOTIFY_TOKEN="あなたのLINE Notifyトークン"

# スクリプトを実行
python main.py
```

## ライセンス

MIT License
