# したらば掲示板→LINE自動送信システム 実装設計書
## Claude Code 実装用 完全版

---

## 📋 プロジェクト概要

**目的**: したらばVALORANT 2代目掲示板から条件に合うスレッドを自動取得し、毎日夜12時にLINEで通知する

**実行環境**: GitHub Actions（完全無料、サーバー不要）

---

## 🎯 実装する機能

### 1. スレッド自動取得
- 対象掲示板: https://jbbs.shitaraba.net/netgame/16797/
- 条件:
  - スレ名が「VALORANT part～～～～」
  - レス数が300以上
  - 最新のスレッドを選択

### 2. レス本文抽出
- HTMLから`<dd>`タグの本文のみを抽出
- 除外するもの:
  - アンカー (`>>123`, `>>123-456`)
  - URL (`http://...`, `https://...`)
  - 投稿者情報・日時（`<dt>`タグ内）

### 3. LINE通知
- LINE Notify を使用
- 最初の20レスをテキストで送信
- フォーマット:
  ```
  📄 VALORANT part1925(2763)
  ━━━━━━━━━━━━━━
  （レス本文1）
  
  （レス本文2）
  
  ...
  ━━━━━━━━━━━━━━
  （全2763件中20件を表示）
  ```

### 4. 自動実行
- GitHub Actions で毎日 00:00 JST（15:00 UTC）に実行
- 手動実行も可能

---

## 📁 ファイル構成

```
shitaraba-line-bot/
├── .github/
│   └── workflows/
│       └── daily_scrape.yml        # GitHub Actions 設定
├── shitaraba_extractor.py          # スクレイピング処理
├── line_sender.py                  # LINE送信処理
├── main.py                         # メイン統合スクリプト
├── requirements.txt                # 依存ライブラリ（既存）
├── .gitignore                      # Git除外設定（既存）
└── README.md                       # セットアップ手順
```

---

## 💻 実装仕様

### shitaraba_extractor.py

**役割**: したらば掲示板からスレッドとレスを取得

**主要関数**:

```python
def get_latest_valorant_thread() -> dict | None:
    """
    条件に合う最新のVALORANTスレッドを取得
    
    処理フロー:
    1. https://jbbs.shitaraba.net/bbs/subject.cgi/netgame/16797/ にアクセス
    2. HTMLをEUC-JPでデコード
    3. <a>タグからスレッド一覧を取得
    4. 正規表現で「VALORANT part(\d+)\((\d+)\)」にマッチするものを抽出
    5. レス数が300以上のものをフィルタ
    6. パート番号が最大のものを返す
    
    戻り値:
    {
        'name': 'VALORANT part1925(2763)',
        'url': 'https://jbbs.shitaraba.net/bbs/read.cgi/netgame/16797/...',
        'part': 1925,
        'posts': 2763
    }
    または None（該当なし）
    """

def extract_post_bodies(thread_url: str) -> list[str]:
    """
    スレッドURLからレス本文のみを抽出
    
    処理フロー:
    1. スレッドURLにアクセス
    2. HTMLをEUC-JPでデコード
    3. <dd>タグをすべて取得
    4. 各<dd>のテキストをclean_text()で整形
    5. 空でないもののみリストに追加
    
    戻り値: ['レス1本文', 'レス2本文', ...]
    """

def clean_text(text: str) -> str:
    """
    レステキストから不要要素を除去
    
    処理:
    1. アンカー除去: re.sub(r'>>\d+(-\d+)?', '', text)
    2. URL除去: re.sub(r'https?://[^\s]+', '', text)
    3. 連続空白を1つに: re.sub(r'\s+', ' ', text)
    4. 前後の空白を削除: text.strip()
    
    戻り値: クリーニング済みテキスト
    """
```

**エラーハンドリング**:
- `requests.get()` は `timeout=10` を設定
- 例外発生時は空のリストまたはNoneを返す
- コンソールにエラーメッセージを出力

**エンコーディング**:
- したらば掲示板は **EUC-JP** を使用
- `response.encoding = 'EUC-JP'` を必ず設定

---

### line_sender.py

**役割**: LINE Notify API経由でメッセージ送信

**主要関数**:

```python
def send_line_notify(message: str, token: str) -> bool:
    """
    LINE Notify でメッセージを送信
    
    API仕様:
    - URL: https://notify-api.line.me/api/notify
    - Method: POST
    - Headers: {'Authorization': f'Bearer {token}'}
    - Data: {'message': message}
    
    引数:
    - message: 送信するテキスト（最大1000文字推奨）
    - token: LINE Notify トークン（環境変数から取得）
    
    戻り値:
    - True: 送信成功（status_code == 200）
    - False: 送信失敗
    
    エラーハンドリング:
    - status_code が 200 以外の場合はエラーメッセージを出力
    - 例外発生時はFalseを返す
    """
```

**メッセージフォーマット例**:
```
📄 VALORANT part1925(2763)
━━━━━━━━━━━━━━
今日の試合めっちゃ熱かったな

フィジカル強すぎて笑う

このマップ苦手なんだよな
...
━━━━━━━━━━━━━━
（全2763件中20件を表示）
```

---

### main.py

**役割**: 全体の処理を統合・実行

**処理フロー**:

```python
import os
from shitaraba_extractor import get_latest_valorant_thread, extract_post_bodies
from line_sender import send_line_notify

def main():
    """
    メイン処理
    
    フロー:
    1. 環境変数 LINE_NOTIFY_TOKEN を取得
    2. get_latest_valorant_thread() でスレッド取得
    3. 該当スレッドがない場合は警告をLINEに送信して終了
    4. extract_post_bodies() でレス取得
    5. 最初の20レスを '\n\n' で結合
    6. フォーマットしてLINEに送信
    """
```

**実装詳細**:
```python
def main():
    print("=" * 60)
    print("したらば→LINE 自動送信システム")
    print("=" * 60)
    
    # 環境変数取得
    line_token = os.getenv("LINE_NOTIFY_TOKEN")
    if not line_token:
        print("✗ エラー: LINE_NOTIFY_TOKEN が設定されていません")
        return
    
    # スレッド取得
    print("\nスレッド一覧を取得中...")
    thread = get_latest_valorant_thread()
    
    if not thread:
        send_line_notify("⚠️ 条件に合うVALORANTスレッドが見つかりませんでした", line_token)
        return
    
    print(f"✓ 対象スレッド: {thread['name']}")
    
    # レス取得
    print("\nレスを取得中...")
    posts = extract_post_bodies(thread['url'])
    
    if not posts:
        send_line_notify("⚠️ レスの取得に失敗しました", line_token)
        return
    
    print(f"✓ {len(posts)}件のレスを取得")
    
    # メッセージ作成（最初の20レス）
    preview_posts = posts[:20]
    preview_text = "\n\n".join(preview_posts)
    
    message = (
        f"📄 {thread['name']}\n"
        f"━━━━━━━━━━━━━━\n"
        f"{preview_text}\n"
        f"━━━━━━━━━━━━━━\n"
        f"（全{len(posts)}件中{len(preview_posts)}件を表示）"
    )
    
    # LINE送信
    print("\nLINEに送信中...")
    success = send_line_notify(message, line_token)
    
    if success:
        print("✓ LINE送信成功")
    else:
        print("✗ LINE送信失敗")
    
    print("\n" + "=" * 60)
    print("処理完了")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

---

### .github/workflows/daily_scrape.yml

**役割**: GitHub Actions の自動実行設定

**実装内容**:

```yaml
name: 毎日0時にしたらばスレッド取得→LINE送信

on:
  schedule:
    # 毎日 15:00 UTC = 日本時間 00:00（夜12時）
    - cron: '0 15 * * *'
  
  # 手動実行も可能
  workflow_dispatch:

jobs:
  scrape-and-send:
    runs-on: ubuntu-latest
    
    steps:
      # リポジトリをチェックアウト
      - name: Checkout repository
        uses: actions/checkout@v3
      
      # Python 3.10 をセットアップ
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      # 依存ライブラリをインストール
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      # メインスクリプトを実行
      - name: Run scraper and send to LINE
        env:
          LINE_NOTIFY_TOKEN: ${{ secrets.LINE_NOTIFY_TOKEN }}
        run: |
          python main.py
```

**ポイント**:
- `cron: '0 15 * * *'` = UTC 15:00 = JST 00:00（夜12時）
- `secrets.LINE_NOTIFY_TOKEN` は GitHub Secrets から取得
- `workflow_dispatch` で手動実行可能

---

### README.md

**内容**: セットアップ手順と使い方

```markdown
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

## ライセンス

MIT License
```

---

## 🔧 技術的な実装ポイント

### 1. エンコーディング処理

```python
response = requests.get(url)
response.encoding = 'EUC-JP'  # したらば掲示板は EUC-JP
```

### 2. 正規表現パターン

```python
# スレッド名のパース
re.match(r'VALORANT part(\d+)\((\d+)\)', thread_name)

# アンカー除去
re.sub(r'>>\d+(-\d+)?', '', text)

# URL除去
re.sub(r'https?://[^\s]+', '', text)
```

### 3. エラーハンドリング

```python
try:
    response = requests.get(url, timeout=10)
    # 処理
except Exception as e:
    print(f"エラー: {e}")
    return None
```

### 4. 環境変数の取得

```python
import os
token = os.getenv("LINE_NOTIFY_TOKEN")
```

---

## ✅ 実装チェックリスト

### shitaraba_extractor.py
- [ ] `get_latest_valorant_thread()` 関数
- [ ] `extract_post_bodies()` 関数
- [ ] `clean_text()` 関数
- [ ] エンコーディング設定（EUC-JP）
- [ ] 正規表現パターン
- [ ] エラーハンドリング

### line_sender.py
- [ ] `send_line_notify()` 関数
- [ ] LINE Notify API呼び出し
- [ ] エラーハンドリング

### main.py
- [ ] 環境変数取得
- [ ] 処理フロー実装
- [ ] メッセージフォーマット
- [ ] エラー時のLINE通知

### .github/workflows/daily_scrape.yml
- [ ] スケジュール設定（cron）
- [ ] 手動実行設定（workflow_dispatch）
- [ ] Python環境セットアップ
- [ ] 依存ライブラリインストール
- [ ] 環境変数の渡し方

### README.md
- [ ] プロジェクト概要
- [ ] セットアップ手順
- [ ] カスタマイズ方法
- [ ] トラブルシューティング

---

## 🎯 実装時の注意点

### 必須事項
1. **EUC-JPエンコーディング**: したらば掲示板は必ずEUC-JPでデコード
2. **タイムアウト設定**: `requests.get(url, timeout=10)`
3. **環境変数チェック**: LINE_NOTIFY_TOKEN の存在確認
4. **エラー時のLINE通知**: 取得失敗時もLINEで通知

### 推奨事項
1. **ログ出力**: 処理の各ステップでprint()
2. **戻り値の型アノテーション**: `-> dict | None` など
3. **docstring**: 各関数に説明を記載
4. **コメント**: 複雑な処理には日本語コメント

### テスト方法
1. **ローカルでテスト**:
   ```bash
   export LINE_NOTIFY_TOKEN="あなたのトークン"
   python main.py
   ```

2. **GitHub Actions手動実行**:
   - Actions タブ → Run workflow

---

## 📊 期待される動作

### 成功時のログ例
```
============================================================
したらば→LINE 自動送信システム
============================================================

スレッド一覧を取得中...
✓ 対象スレッド: VALORANT part1925(2763)

レスを取得中...
✓ 2763件のレスを取得

LINEに送信中...
✓ LINE送信成功

============================================================
処理完了
============================================================
```

### LINE通知例
```
📄 VALORANT part1925(2763)
━━━━━━━━━━━━━━
今日の試合めっちゃ熱かったな

フィジカル強すぎて笑う

このマップ苦手なんだよな

エージェント何使ってる？

（以下、20レス分続く）
━━━━━━━━━━━━━━
（全2763件中20件を表示）
```

---

## 🚀 実装完了後の確認事項

1. [ ] すべてのファイルが正しく作成されている
2. [ ] `requirements.txt` に依存関係が記載されている
3. [ ] `.gitignore` に `.env` などが記載されている
4. [ ] README.md に使い方が記載されている
5. [ ] ローカルでテスト実行してLINEに通知が届く
6. [ ] GitHubにプッシュ済み
7. [ ] GitHub Secrets に LINE_NOTIFY_TOKEN を設定済み
8. [ ] GitHub Actions で手動実行して成功

---

## 📝 補足情報

### したらば掲示板のURL構造

**スレッド一覧**:
```
https://jbbs.shitaraba.net/bbs/subject.cgi/netgame/16797/
```

**個別スレッド**:
```
https://jbbs.shitaraba.net/bbs/read.cgi/netgame/16797/1748243747/
                                                          └─ スレッドID
```

### HTML構造

```html
<!-- スレッド一覧 -->
<a href="/bbs/read.cgi/netgame/16797/1748243747/">VALORANT part1925(2763)</a>

<!-- 個別スレッド -->
<dt>1 名前：名無しさん 投稿日：2025/01/26(日) 12:34:56</dt>
<dd>これがレス本文です >>123 http://example.com</dd>
```

---

これですべての実装仕様が揃いました。Claude Codeにこの設計書を渡せば、完璧に動作するシステムが完成します！🎉
