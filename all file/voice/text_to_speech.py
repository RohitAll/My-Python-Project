"""
Text-to-Speech (TTS) Subsystem
Defines TextToSpeechProvider abstraction and implementations (PyTTSx3 offline, EdgeTTS online).
"""

import abc
import asyncio
import logging
import os
import re
import tempfile
from typing import Optional
from config.settings import settings

logger = logging.getLogger("JARVIS.Voice.TTS")


def clean_text_for_speech(text: str) -> str:
    """Sanitize raw markdown/JSON text into clean spoken sentences."""
    if not text:
        return ""
    # Strip markdown code blocks ```...```
    cleaned = re.sub(r"```[\s\S]*?```", "", text)
    # Strip JSON objects {...}
    cleaned = re.sub(r"\{[\s\S]*?\}", "", cleaned)
    # Strip markdown headers, bold, italics, backticks
    cleaned = re.sub(r"[\*\_`#]", "", cleaned)
    # Strip status symbols
    cleaned = (
        cleaned.replace("✓", "Action completed.")
        .replace("✗", "Action failed.")
        .replace("→", "In progress.")
    )
    # Collapse extra whitespace
    cleaned = " ".join(cleaned.split()).strip()
    return cleaned


class TextToSpeechProvider(abc.ABC):
    """Abstract base class for TTS engines."""

    @abc.abstractmethod
    async def speak(self, text: str):
        """Synthesize and play audio for text."""
        pass


class PyTTSx3Provider(TextToSpeechProvider):
    """Offline TTS Provider using pyttsx3 with SAPI5 COM thread initialization."""

    def __init__(self):
        self._voice_id = None
        self._find_voice()

    def _find_voice(self):
        try:
            import pyttsx3

            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            for v in voices:
                if "david" in v.name.lower() or "male" in v.name.lower() or "christopher" in v.name.lower():
                    self._voice_id = v.id
                    break
        except Exception as e:
            logger.warning("Could not query pyttsx3 voices: %s", e)

    async def speak(self, text: str):
        spoken_text = clean_text_for_speech(text)
        if not spoken_text:
            return

        def _run_speak():
            try:
                try:
                    import pythoncom

                    pythoncom.CoInitialize()
                except Exception:
                    pass

                import pyttsx3

                engine = pyttsx3.init()
                engine.setProperty("rate", 175)
                engine.setProperty("volume", 1.0)
                if self._voice_id:
                    try:
                        engine.setProperty("voice", self._voice_id)
                    except Exception:
                        pass
                engine.say(spoken_text)
                engine.runAndWait()
            except Exception as e:
                logger.error("pyttsx3 speak error: %s", e)
            finally:
                try:
                    import pythoncom

                    pythoncom.CoUninitialize()
                except Exception:
                    pass

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _run_speak)


class EdgeTTSProvider(TextToSpeechProvider):
    """High-quality Online Neural TTS Provider using edge-tts and pygame audio player."""

    def __init__(self, voice: str = "hi-IN-MadhurNeural"):
        self.voice = voice or "hi-IN-MadhurNeural"

    async def speak(self, text: str):
        spoken_text = clean_text_for_speech(text)
        if not spoken_text:
            return

        try:
            import edge_tts
            import pygame

            temp_path = os.path.join(
                tempfile.gettempdir(), f"jarvis_tts_{os.getpid()}_{hash(spoken_text) & 0xffff}.mp3"
            )

            communicate = edge_tts.Communicate(spoken_text, self.voice)
            await communicate.save(temp_path)

            def _play_audio():
                try:
                    if not pygame.mixer.get_init():
                        pygame.mixer.init()
                    pygame.mixer.music.load(temp_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                    pygame.mixer.music.unload()
                except Exception as ex:
                    logger.error("Error playing TTS audio file via pygame: %s", ex)
                finally:
                    if os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except Exception:
                            pass

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _play_audio)
        except Exception as e:
            logger.warning("EdgeTTS failed, falling back to PyTTSx3: %s", e)
            fallback = PyTTSx3Provider()
            await fallback.speak(spoken_text)


def get_tts_provider() -> TextToSpeechProvider:
    voice = settings.TTS_VOICE if settings.TTS_VOICE else "hi-IN-MadhurNeural"
    if settings.TTS_PROVIDER.lower() == "edge-tts":
        return EdgeTTSProvider(voice=voice)
    return PyTTSx3Provider()
