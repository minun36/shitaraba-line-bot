"""
テキストをMP3音声ファイルに変換するモジュール

gTTS (Google Text-to-Speech) を使用して日本語テキストを自然な音声で MP3 に変換します。
Discordのファイルサイズ上限(25MB)も監視します。
"""
import os
from typing import Optional

try:
    from gtts import gTTS
except ImportError:
    gTTS = None


# Discordのファイルサイズ上限（目安）
DISCORD_MAX_SIZE = 25 * 1024 * 1024  # 25MB
LANGUAGE = "ja"  # 日本語


def text_to_mp3(text: str, output_file: str, max_size_mb: int = 25) -> tuple[bool, Optional[int]]:
    """
    テキストをMP3ファイルに変換

    引数:
    - text: 変換するテキスト
    - output_file: 出力先ファイルパス
    - max_size_mb: 最大ファイルサイズ警告値（MB）

    戻り値: (成功フラグ, ファイルサイズ(bytes))
    失敗時または size_warning 時は (False, size) または (True, size) を返す
    """
    if gTTS is None:
        print("エラー: gTTS がインストールされていません")
        print("  pip install gTTS でインストールしてください")
        return False, None

    if not text or not text.strip():
        print("エラー: 空のテキストです")
        return False, None

    try:
        # gTTS でテキスト→音声変換
        tts = gTTS(text=text, lang=LANGUAGE, slow=False)
        tts.save(output_file)

        # ファイルサイズを確認
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            size_mb = size / (1024 * 1024)
            print(f"✓ MP3生成完了: {output_file}")
            print(f"  ファイルサイズ: {size_mb:.2f} MB ({size} bytes)")

            if size > max_size_mb * 1024 * 1024:
                print(f"⚠️  警告: ファイルサイズが {max_size_mb}MB を超えています")
                print(f"   Discordで送信できない可能性があります")
                return True, size  # 生成は成功したが警告

            return True, size
        else:
            print(f"エラー: ファイル生成に失敗しました")
            return False, None

    except Exception as e:
        print(f"エラー: text_to_mp3(): {e}")
        return False, None


if __name__ == '__main__':
    # 簡単なテスト
    test_text = "これはテスト音声です。日本語の読み上げがうまく機能しているか確認しています。"
    result, size = text_to_mp3(test_text, "test_output.mp3")
    print(f"Result: {result}, Size: {size}")
