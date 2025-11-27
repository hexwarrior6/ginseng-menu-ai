#!/usr/bin/env python3
"""
Text-to-Speech utility module
Using EdgeTTS for voice synthesis
"""

import os
import asyncio
import logging
from edge_tts import Communicate
import pygame
import tempfile
from typing import Optional


async def text_to_speech_async(text: str, voice: str = "en-US-AriaNeural") -> bool:
    """
    Asynchronously convert text to speech using EdgeTTS and play it
    
    Args:
        text (str): Text to convert to speech
        voice (str): Voice model to use, default is "en-US-AriaNeural"
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not text or not text.strip():
        logging.warning("Text to speech: empty text provided")
        return False

    temp_filename = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            temp_filename = tmp_file.name

        # Generate speech using EdgeTTS
        communicate = Communicate(text, voice)
        await communicate.save(temp_filename)

        # Play the audio file
        success = await play_audio_async(temp_filename)
        return success

    except Exception as e:
        logging.error(f"Error in text_to_speech_async: {e}")
        return False
    finally:
        # Clean up temporary file
        if temp_filename and os.path.exists(temp_filename):
            try:
                os.unlink(temp_filename)
            except Exception as e:
                logging.warning(f"Could not remove temporary file {temp_filename}: {e}")


async def play_audio_async(filename: str) -> bool:
    """
    Asynchronously play an audio file using pygame
    
    Args:
        filename (str): Path to the audio file to play
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Initialize pygame mixer
        pygame.mixer.init()

        # Load and play audio
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)

        return True
    except Exception as e:
        logging.error(f"Error in play_audio_async: {e}")
        return False
    finally:
        # Quit pygame mixer
        try:
            pygame.mixer.quit()
        except:
            pass


def text_to_speech(text: str, voice: str = "en-US-AriaNeural") -> bool:
    """
    Synchronous function to convert text to speech using EdgeTTS and play it
    
    Args:
        text (str): Text to convert to speech
        voice (str): Voice model to use, default is "en-US-AriaNeural"
        
    Returns:
        bool: True if successful, False otherwise
    """
    return asyncio.run(text_to_speech_async(text, voice))


# Predefined voice options
VOICE_OPTIONS = {
    "male_us": "en-US-GuyNeural",          # US male voice
    "female_us": "en-US-AriaNeural",       # US female voice
    "male_uk": "en-GB-RyanNeural",         # UK male voice
    "female_uk": "en-GB-SoniaNeural",      # UK female voice
}


if __name__ == "__main__":
    # Test the text to speech functionality
    test_text = "Hello, this is a test of text to speech using Edge TTS."
    
    logging.basicConfig(level=logging.INFO)
    
    success = text_to_speech(test_text, VOICE_OPTIONS["female_us"])
    if success:
        print("✅ Text to speech test completed successfully")
    else:
        print("❌ Text to speech test failed")