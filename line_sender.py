import requests


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
    try:
        url = "https://notify-api.line.me/api/notify"
        headers = {'Authorization': f'Bearer {token}'}
        data = {'message': message}
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            return True
        else:
            print(f"✗ LINE Notify エラー: ステータスコード {response.status_code}")
            print(f"  レスポンス: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ LINE Notify 送信エラー: {e}")
        return False
