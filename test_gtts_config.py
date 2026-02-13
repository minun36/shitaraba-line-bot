#!/usr/bin/env python3
"""gTTS のパラメータと制限事項を調査"""

from gtts import gTTS
import inspect

print("=" * 60)
print("gTTS パラメータ調査")
print("=" * 60)

# gTTS.__init__ のシグネチャを確認
sig = inspect.signature(gTTS.__init__)
print("\n【gTTS.__init__ パラメータ】")
for param_name, param in sig.parameters.items():
    if param_name not in ['self', 'args', 'kwargs']:
        default_val = param.default if param.default != inspect.Parameter.empty else "必須"
        print(f"  {param_name}: {default_val}")

# MAX_CHARS の確認
print(f"\n【テキスト制限】")
print(f"  GOOGLE_TTS_MAX_CHARS: {gTTS.GOOGLE_TTS_MAX_CHARS}")

# slow パラメータのテスト
print(f"\n【読み上げ速度】")
print(f"  slow=False: 通常速度（デフォルト）")
print(f"  slow=True: 遅い速度（API側の制限）")
print(f"  ※ gTTS では slow パラメータのみで、カスタムスピードはサポートなし")

# ボイス設定についての確認
print(f"\n【ボイス/言語】")
print(f"  lang='ja': 日本語（デフォルト）")
print(f"  tld='co.jp': TLD（トップレベルドメイン）：通常は自動")
print(f"  ※ gTTS では Google が自動的に適切なボイスを選択")
print(f"  ※ 特定のボイス指定はサポートされていません")

print("\n" + "=" * 60)
