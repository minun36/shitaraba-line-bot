"""
メイン統合スクリプト

実行フロー:
 - 環境変数から `DISCORD_BOT_TOKEN`, `DISCORD_CHANNEL_ID` を取得
 - `get_latest_valorant_thread()` で対象スレッドを取得
 - `extract_post_bodies()` でレスを取得
 - 最初の20レスを結合して Discord に送信

エラー時にはコンソールと Discord（可能なら）に通知します。
"""
import os
from shitaraba_extractor import get_latest_valorant_thread, extract_post_bodies
from discord_sender import send_discord_message, send_discord_file
import os
from datetime import datetime
from pathlib import Path


MAX_DISCORD_MESSAGE = 1900


def build_message(thread: dict, posts: list[str]) -> str:
    """
    メッセージをフォーマットして返す
    """
    preview_posts = posts[:20]
    preview_text = "\n\n".join(preview_posts)

    header = f"📄 {thread['name']}\n━━━━━━━━━━━━━━"
    footer = f"━━━━━━━━━━━━━━\n（全{len(posts)}件中{len(preview_posts)}件を表示）"

    message = f"{header}\n{preview_text}\n{footer}"

    # Discord の制限に収まるようにトリム
    if len(message) > MAX_DISCORD_MESSAGE:
        allowed = MAX_DISCORD_MESSAGE - len(header) - len(footer) - 20
        if allowed > 0:
            trimmed_preview = preview_text[:allowed].rstrip()
            message = f"{header}\n{trimmed_preview}\n...\n{footer}"
        else:
            # 最悪ヘッダのみ送る
            message = f"{header}\n{footer}"

    return message


def main():
    print("=" * 60)
    print("したらば→Discord 自動送信システム")
    print("=" * 60)

    discord_token = os.getenv('DISCORD_BOT_TOKEN')
    discord_channel = os.getenv('DISCORD_CHANNEL_ID')
    if not discord_token or not discord_channel:
        print("✗ エラー: DISCORD_BOT_TOKEN または DISCORD_CHANNEL_ID が設定されていません")
        return

    print("\nスレッド一覧を取得中...")
    thread = get_latest_valorant_thread()
    if not thread:
        print("⚠️ 条件に合うVALORANTスレッドが見つかりませんでした")
        # 可能なら Discord に送信
        send_discord_message("⚠️ 条件に合うVALORANTスレッドが見つかりませんでした", discord_token, discord_channel)
        return

    print(f"✓ 対象スレッド: {thread['name']}")

    print("\nレスを取得中...")
    posts = extract_post_bodies(thread['url'], expected_posts=thread.get('posts'))
    if not posts:
        print("⚠️ レスの取得に失敗しました")
        send_discord_message("⚠️ レスの取得に失敗しました", discord_token, discord_channel)
        return

    print(f"✓ {len(posts)}件のレスを取得")

    # 全レスをテキストファイルに出力
    outdir = Path('outputs')
    outdir.mkdir(exist_ok=True)

    # スレッドIDをURLから抽出
    thread_id = 'unknown'
    try:
        m = __import__('re').search(r'/bbs/read\.cgi/[^/]+/(\d+)/', thread['url'])
        if m:
            thread_id = m.group(1)
    except Exception:
        pass

    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    filename = outdir / f"valorant_part{thread.get('part')}_{thread_id}_{timestamp}.txt"
    try:
        with filename.open('w', encoding='utf-8') as f:
            f.write(f"{thread['name']}\n")
            f.write('\n')
            f.write('\n\n'.join(posts))
        print(f"✓ テキストファイル出力: {filename}")
    except Exception as e:
        print(f"✗ ファイル出力失敗: {e}")

    # Discordには生成したテキストファイルを添付して送信（これが唯一の出力）
    message_caption = f"📄 {thread['name']} (全{len(posts)}件)"
    print(f"\nDiscordにファイル添付を送信中...: {filename}")
    success = send_discord_file(str(filename), discord_token, discord_channel, message=message_caption)

    if success:
        print("✓ Discord送信成功")
    else:
        print("✗ Discord送信失敗")

    print("\n" + "=" * 60)
    print("処理完了")
    print("=" * 60)


if __name__ == '__main__':
    main()
