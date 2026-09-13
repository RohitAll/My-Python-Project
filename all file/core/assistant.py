"""
JARVIS Core Assistant Coordinator
Connects UI signals, AI Orchestration, Voice Input/Output, and Status State Transitions.
"""

import asyncio
import logging
from enum import Enum
from typing import Optional, Callable, Dict, Any

from config.settings import settings
from core.orchestrator import orchestrator
from voice.speech_to_text import get_stt_provider
from voice.text_to_speech import get_tts_provider
from voice.wake_word import wake_word_listener

logger = logging.getLogger("JARVIS.Core.Assistant")


class AssistantState(Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    SPEAKING = "SPEAKING"
    EXECUTING = "EXECUTING"
    ERROR = "ERROR"


class JarvisAssistant:
    """Master assistant engine controlling state transitions and execution loops."""

    def __init__(self):
        self.state = AssistantState.IDLE
        self.stt_provider = get_stt_provider()

        self._state_callback: Optional[Callable[[AssistantState], None]] = None
        self._response_callback: Optional[Callable[[Dict[str, Any]], None]] = None

    def register_callbacks(
        self,
        state_callback: Callable[[AssistantState], None],
        response_callback: Callable[[Dict[str, Any]], None],
    ):
        """Register PySide6 UI listeners for state changes and responses."""
        self._state_callback = state_callback
        self._response_callback = response_callback

    def set_state(self, new_state: AssistantState):
        """Update assistant state and notify UI."""
        self.state = new_state
        logger.info("Assistant state updated -> %s", new_state.value)
        if self._state_callback:
            try:
                self._state_callback(new_state)
            except Exception as e:
                logger.error("Error updating UI state callback: %s", e)

    async def handle_text_command(self, text: str):
        """Process user text command through orchestrator."""
        if not text.strip():
            return

        self.set_state(AssistantState.THINKING)

        try:
            # Progress callback for multi-step tasks
            def task_progress_cb(plan_dict, current_step_dict):
                if current_step_dict:
                    self.set_state(AssistantState.EXECUTING)

            result = await orchestrator.process_user_input(text, progress_callback=task_progress_cb)

            response_text = result.get("response", "")

            # Trigger response callback to UI
            if self._response_callback:
                self._response_callback(result)

            # Speak response if voice enabled
            if settings.ENABLE_VOICE and response_text:
                self.set_state(AssistantState.SPEAKING)
                await get_tts_provider().speak(response_text)

            self.set_state(AssistantState.IDLE)
        except Exception as e:
            logger.error("Error processing text command: %s", e, exc_info=True)
            self.set_state(AssistantState.ERROR)
            if self._response_callback:
                self._response_callback(
                    {"type": "error", "response": f"An error occurred: {str(e)}", "success": False}
                )
            await asyncio.sleep(2)
            self.set_state(AssistantState.IDLE)

    async def start_listening_voice(self):
        """Listen from microphone and process command."""
        self.set_state(AssistantState.LISTENING)
        transcription = await self.stt_provider.transcribe_microphone()

        if transcription:
            logger.info("Voice transcription received: '%s'", transcription)
            await self.handle_text_command(transcription)
        else:
            self.set_state(AssistantState.IDLE)

    def init_wake_word(self):
        """Initialize wake word listener with response callback."""

        async def _wake_word_triggered():
            logger.info("Wake word triggered!")
            self.set_state(AssistantState.SPEAKING)
            await get_tts_provider().speak("Yes, how can I help?")
            await self.start_listening_voice()

        wake_word_listener.set_callback(_wake_word_triggered)
        if settings.WAKE_WORD_ENABLED:
            wake_word_listener.start()


jarvis_assistant = JarvisAssistant()
