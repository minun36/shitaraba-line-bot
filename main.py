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
        print("✗ スレッドが見つかりません")
        return
    
    print(f"✓ 対象スレッド: {thread['name']}")
    
    # レス取得
    print("\nレスを取得中...")
    posts = extract_post_bodies(thread['url'])
    
    if not posts:
        send_line_notify("⚠️ レスの取得に失敗しました", line_token)
        print("✗ レスの取得に失敗しました")
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
