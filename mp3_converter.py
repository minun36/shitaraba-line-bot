"""
テキストをMP3音声ファイルに変換するモジュール

gTTS (Google Text-to-Speech) を使用して日本語テキストを自然な音声で MP3 に変換します。
大量テキストはチャンクに分割して複数のMP3を生成し、レート制限を回避します。
Discordのファイルサイズ上限(25MB)も監視します。
"""
import os
import time
import warnings
from typing import Optional
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# SSL警告を抑制（ローカルシステムのSSL証明書問題対策）
warnings.filterwarnings("ignore", message="Unverified HTTPS request is being made")
warnings.simplefilter('ignore', InsecureRequestWarning)
urllib3.disable_warnings(InsecureRequestWarning)

# グローバルにSSL検証をスキップ
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

try:
    from gtts import gTTS
except ImportError:
    gTTS = None


# Discordのファイルサイズ上限（目安）
DISCORD_MAX_SIZE = 25 * 1024 * 1024  # 25MB
LANGUAGE = "ja"  # 日本語

# テキスト分割用パラメータ（文字数単位）
# gTTS は内部で 100文字ごとに自動分割するため、大きなチャンクでも問題なし
CHUNK_SIZE = 10000  # 1チャンク = 10000文字（分割数を削減して高速化）
RETRY_DELAY = 3     # リトライ間隔（秒）
MAX_RETRIES = 5     # 最大リトライ回数を増加
TLD = 'co.jp'       # 日本語ボイスを優先


def text_to_mp3(text: str, output_file: str, max_size_mb: int = 25) -> tuple[bool, Optional[int]]:
    """
    テキストをMP3ファイルに変換（大量テキストはチャンク分割対応）

    引数:
    - text: 変換するテキスト
    - output_file: 出力先ファイルパス（複数生成時は _part1.mp3 等に自動分割）
    - max_size_mb: 最大ファイルサイズ警告値（MB）

    戻り値: (成功フラグ, ファイルサイズ(bytes))
    失敗時は (False, None) を返す
    """
    if gTTS is None:
        print("エラー: gTTS がインストールされていません")
        print("  pip install gTTS でインストールしてください")
        return False, None

    if not text or not text.strip():
        print("エラー: 空のテキストです")
        return False, None

    # テキストをチャンクに分割
    chunks = _split_text_into_chunks(text, CHUNK_SIZE)
    print(f"テキストを {len(chunks)} 個のチャンクに分割します")

    if len(chunks) == 1:
        # 単一ファイル生成
        return _convert_chunk(chunks[0], output_file, max_size_mb)
    else:
        # 複数ファイル生成
        base_name, ext = os.path.splitext(output_file)
        total_size = 0
        success = True

        for idx, chunk in enumerate(chunks, 1):
            chunk_file = f"{base_name}_part{idx}{ext}"
            result, size = _convert_chunk(chunk, chunk_file, max_size_mb)
            if result and size:
                total_size += size
            else:
                success = False
                print(f"警告: チャンク {idx} の生成に失敗しました")

        if success:
            print(f"\n✓ 全 {len(chunks)} チャンクの MP3 生成完了")
            print(f"  合計ファイルサイズ: {total_size / (1024 * 1024):.2f} MB")
            return True, total_size
        else:
            return False, None


def _split_text_into_chunks(text: str, chunk_size: int) -> list[str]:
    """
    テキストを指定サイズのチャンクに分割（句点で区切る）

    引数:
    - text: 分割するテキスト
    - chunk_size: 目標チャンクサイズ（文字数）

    戻り値: チャンクのリスト
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    current_chunk = ""

    # 句点で分割（。で区切る）
    sentences = text.split("。")

    for sentence in sentences:
        if not sentence.strip():
            continue

        sentence_with_period = sentence + "。"

        # チャンクが満杯の場合は新規チャンクへ
        if len(current_chunk) + len(sentence_with_period) > chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = sentence_with_period
        else:
            current_chunk += sentence_with_period

    # 残りのテキストを追加
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def _convert_chunk(text: str, output_file: str, max_size_mb: int, retry_count: int = 0) -> tuple[bool, Optional[int]]:
    """
    単一テキストをMP3に変換（リトライ対応）

    引数:
    - text: 変換するテキスト
    - output_file: 出力先ファイルパス
    - max_size_mb: 最大ファイルサイズ警告値（MB）
    - retry_count: 現在のリトライ回数（内部用）

    戻り値: (成功フラグ, ファイルサイズ(bytes))
    """
    try:
        # gTTS でテキスト→音声変換
        # slow=False で通常速度（最速）、tld='co.jp' で日本語ボイスを優先
        tts = gTTS(text=text, lang=LANGUAGE, slow=False, tld=TLD, timeout=8)
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
                return True, size

            return True, size
        else:
            print(f"エラー: ファイル生成に失敗しました")
            return False, None

    except (KeyboardInterrupt, TimeoutError) as e:
        # SSL 証明書読み込みのハングやタイムアウトの場合はリトライ
        if retry_count < MAX_RETRIES:
            print(f"⚠️  SSL 証明書エラー検出。{RETRY_DELAY}秒後にリトライ... ({retry_count + 1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
            return _convert_chunk(text, output_file, max_size_mb, retry_count + 1)
        else:
            print(f"エラー: _convert_chunk(): {type(e).__name__}: SSL 証明書エラーが解決できません")
            return False, None

    except Exception as e:
        error_msg = str(e)
        # 429 エラー（レート制限）の場合はリトライ
        if "429" in error_msg and retry_count < MAX_RETRIES:
            print(f"⚠️  レート制限検出。{RETRY_DELAY}秒後に リトライ... ({retry_count + 1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
            return _convert_chunk(text, output_file, max_size_mb, retry_count + 1)

        print(f"エラー: _convert_chunk(): {e}")
        return False, None


if __name__ == '__main__':
    # 簡単なテスト
    test_text = "これはテスト音声です。日本語の読み上げがうまく機能しているか確認しています。"
    result, size = text_to_mp3(test_text, "test_output.mp3")
    print(f"Result: {result}, Size: {size}")
