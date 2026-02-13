#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug edge-tts with verbose output
"""
import asyncio
import edge_tts
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def test():
    try:
        text = "これはテストです。"
        print(f"Text: {text}")
        print(f"Voice: ja-JP-NanaNeural")
        
        communicate = edge_tts.Communicate(text=text, voice="ja-JP-NanaNeural")
        sub_manager = communicate.stream_generator()
        print(f"Stream manager: {sub_manager}")
        
        await communicate.save("test_direct.mp3")
        print("✓ Success! Generated test_direct.mp3")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
