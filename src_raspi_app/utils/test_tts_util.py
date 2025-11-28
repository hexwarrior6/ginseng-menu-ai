#!/usr/bin/env python3
"""
Test script for TTS utility
"""

from utils.tts_util import text_to_speech, VOICE_OPTIONS


def test_tts_basic():
    """Test basic TTS functionality"""
    print("Testing basic TTS functionality...")

    test_text = "Hello, this is a test of the text to speech system on Raspberry Pi using Edge TTS."
    text_to_speech(test_text, VOICE_OPTIONS["female_us"])


if __name__ == "__main__":
    test_tts_basic()