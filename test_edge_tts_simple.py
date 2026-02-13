#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple edge-tts test
"""
import asyncio
import edge_tts

async def test():
    try:
        text = "これはテストです。音声合成がうまく機能しているか確認しています。"
        print(f"Converting text to speech...")
        communicate = edge_tts.Communicate(text=text, voice="ja-JP-NanaNeural")
        await communicate.save("test_direct.mp3")
        print("✓ Success! generated test_direct.mp3")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test())
