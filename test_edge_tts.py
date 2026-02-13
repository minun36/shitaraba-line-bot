#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Direct test for edge-tts
"""
import asyncio
import edge_tts

async def test():
    try:
        text = "これはテストです。"
        communicate = edge_tts.Communicate(text=text, voice="ja-JP-NanaNeural")
        await communicate.save("test_direct.mp3")
        print("✓ Success! Generated test_direct.mp3")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
