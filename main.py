"""
メイン統合スクリプト

実行フロー:
 - 環境変数から `DISCORD_BOT_TOKEN`, `DISCORD_CHANNEL_ID` を取得
 - `get_latest_valorant_thread()` で対象スレッドを取得
 - `extract_post_bodies()` でレスを取得
 - 全レスを結合して MP3 に音声変換
 - Discord にファイル添付で送信

エラー時にはコンソールと Discord（可能なら）に通知します。
"""
import os
import re
from datetime import datetime
from pathlib import Path
from shitaraba_extractor import get_latest_valorant_thread, extract_post_bodies
from discord_sender import send_discord_message, send_discord_file
from mp3_converter import text_to_mp3


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

    # 全レスを結合してMP3に変換
    outdir = Path('outputs')
    outdir.mkdir(exist_ok=True)

    # スレッドIDをURLから抽出
    thread_id = 'unknown'
    try:
        m = re.search(r'/bbs/read\.cgi/[^/]+/(\d+)/', thread['url'])
        if m:
            thread_id = m.group(1)
    except Exception:
        pass

    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    mp3_filename = outdir / f"valorant_part{thread.get('part')}_{thread_id}_{timestamp}.mp3"

    # 全レスをテキストに結合（段落区切り）
    full_text = '\n\n'.join(posts)
    print(f"\nMP3に変換中（{len(posts)}件のレス、{len(full_text)}文字）...")
    success_convert, size = text_to_mp3(full_text, str(mp3_filename))

    if not success_convert:
        print("⚠️ MP3変換に失敗しました")
        send_discord_message("⚠️ MP3変換に失敗しました", discord_token, discord_channel)
        return

    # Discordにファイル添付で送信
    message_caption = f"🎙️ {thread['name']} (全{len(posts)}件)"
    print(f"\nDiscordにMP3ファイルを送信中...: {mp3_filename}")
    success = send_discord_file(str(mp3_filename), discord_token, discord_channel, message=message_caption)

    if success:
        print("✓ Discord送信成功")
    else:
        print("✗ Discord送信失敗")

    print("\n" + "=" * 60)
    print("処理完了")
    print("=" * 60)


if __name__ == '__main__':
    main()
