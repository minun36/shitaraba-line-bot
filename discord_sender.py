"""
Discord へメッセージを送信するユーティリティ

関数:
 - send_discord_message(message: str, token: str, channel_id: str) -> bool

注意: トークンやチャンネルIDは環境変数に保持し、コード中にハードコーディングしないこと。
"""
import json
import time
import requests
from typing import Optional


API_BASE = "https://discord.com/api/v10"


def send_discord_message(message: str, token: str, channel_id: str) -> bool:
    """
    Discord Bot トークンを用いて指定チャンネルにメッセージを送信する

    引数:
    - message: 送信するテキスト（Discord の 2000 文字制限に注意）
    - token: Bot トークン（'Bot <token>' の形式ではなく生のトークンを渡す）
    - channel_id: 送信先チャンネルID

    戻り値: 成功時 True, 失敗時 False

    エラーハンドリング:
    - 429 (rate limit) の場合はリトライを行う
    - その他の HTTP エラーは標準出力に出力して False を返す
    """
    url = f"{API_BASE}/channels/{channel_id}/messages"
    headers = {
        'Authorization': f'Bot {token}',
        'Content-Type': 'application/json'
    }
    payload = {'content': message}

    try:
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        if resp.status_code == 200 or resp.status_code == 201:
            return True
        if resp.status_code == 429:
            # レスポンスに retry_after が入っている
            try:
                info = resp.json()
                wait = float(info.get('retry_after', 1.0))
            except Exception:
                wait = 1.0
            time.sleep(wait)
            # 単純に1回だけリトライ
            resp2 = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
            if resp2.status_code in (200, 201):
                return True
            print(f"Discord送信失敗: status={resp2.status_code}, body={resp2.text}")
            return False

        print(f"Discord送信失敗: status={resp.status_code}, body={resp.text}")
        return False

    except Exception as e:
        print(f"エラー: send_discord_message(): {e}")
        return False


if __name__ == '__main__':
    print('このモジュールは直接実行せず、他から呼び出してください。')
