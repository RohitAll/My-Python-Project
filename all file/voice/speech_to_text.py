"""
Speech-to-Text (STT) Subsystem
Defines SpeechToTextProvider abstraction and implementations with Hindi + English support.
"""

import abc
import asyncio
import logging
from typing import Optional

logger = logging.getLogger("JARVIS.Voice.STT")


class SpeechToTextProvider(abc.ABC):
    """Abstract base class for STT engines."""

    @abc.abstractmethod
    async def transcribe_microphone(self) -> Optional[str]:
        """Listen to user speech from mic and return transcribed text."""
        pass


class SpeechRecognitionProvider(SpeechToTextProvider):
    """STT Provider using speech_recognition library with multi-language (Hindi + English) support."""

    def __init__(self):
        self._recognizer = None
        self._mic = None
        self._init_audio()

    def _init_audio(self):
        try:
            import speech_recognition as sr

            self._recognizer = sr.Recognizer()
            self._recognizer.energy_threshold = 300
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.pause_threshold = 0.8
            self._mic = sr.Microphone()
            with self._mic as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.3)
        except Exception as e:
            logger.warning("Could not initialize microphone or SpeechRecognition: %s", e)

    async def transcribe_microphone(self) -> Optional[str]:
        def _record_and_recognize():
            import speech_recognition as sr

            if not self._recognizer or not self._mic:
                self._init_audio()
                if not self._recognizer or not self._mic:
                    logger.error("Microphone hardware is not accessible.")
                    return None

            try:
                with self._mic as source:
                    logger.info("Listening for voice input...")
                    audio = self._recognizer.listen(source, timeout=7, phrase_time_limit=12)

                logger.info("Processing voice recognition...")

                # Try Hindi STT first
                try:
                    text = self._recognizer.recognize_google(audio, language="hi-IN")
                    if text and text.strip():
                        logger.info("Speech transcribed (Hindi): '%s'", text)
                        return text
                except (sr.UnknownValueError, sr.RequestError):
                    pass

                # Fallback to English STT
                try:
                    text = self._recognizer.recognize_google(audio, language="en-US")
                    if text and text.strip():
                        logger.info("Speech transcribed (English): '%s'", text)
                        return text
                except sr.UnknownValueError:
                    logger.info("Voice not recognized clearly in Hindi or English.")
                    return None

            except sr.WaitTimeoutError:
                logger.info("Voice listening timed out (no speech detected).")
                return None
            except Exception as e:
                logger.error("STT transcription error: %s", e)
                return None

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _record_and_recognize)


def get_stt_provider() -> SpeechToTextProvider:
    return SpeechRecognitionProvider()
