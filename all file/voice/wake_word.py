"""
Wake Word Listener Subsystem
Monitors microphone input in background for trigger phrases like 'Hey JARVIS' or 'JARVIS'.
"""

import asyncio
import logging
from typing import Optional, Callable
from config.settings import settings

logger = logging.getLogger("JARVIS.Voice.WakeWord")


class WakeWordListener:
    """Background listener for wake word triggers."""

    def __init__(self, trigger_phrase: str = "hey jarvis"):
        self.trigger_phrase = trigger_phrase.lower()
        self.is_running = False
        self._callback: Optional[Callable] = None
        self._task: Optional[asyncio.Task] = None

    def set_callback(self, callback: Callable):
        """Set callback to trigger when wake word is detected."""
        self._callback = callback

    def start(self):
        """Start background wake word listening task."""
        if not settings.WAKE_WORD_ENABLED:
            logger.info("Wake word functionality is disabled in settings.")
            return

        if self.is_running:
            return

        self.is_running = True
        self._task = asyncio.create_task(self._listen_loop())
        logger.info("Wake word listener started for trigger: '%s'", self.trigger_phrase)

    def stop(self):
        """Stop background listener."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("Wake word listener stopped.")

    async def _listen_loop(self):
        from voice.speech_to_text import get_stt_provider

        stt = get_stt_provider()
        while self.is_running:
            try:
                text = await stt.transcribe_microphone()
                if text and self.trigger_phrase in text.lower():
                    logger.info("Wake word detected in phrase: '%s'", text)
                    if self._callback:
                        if asyncio.iscoroutinefunction(self._callback):
                            await self._callback()
                        else:
                            self._callback()
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in wake word loop: %s", e)
                await asyncio.sleep(2)


wake_word_listener = WakeWordListener(trigger_phrase=settings.WAKE_WORD)
