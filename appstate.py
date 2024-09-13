"""This module contains only AppState class. It's main class, containing and
uniting all the other code entities. **Very poor architecture design, should
be restructurized and rewritten!**"""

from assistant import Assistant
from intention_classifier import IntentionClassifier
from settings import Settings
from voice_handler import VoiceHandler


class AppState:
    """Simple God-like data class for the application. Contains all the data /
    objects which are used by the program, including the voice handler, intention
    classifier, assistant instance, and settings."""

    voice_handler: VoiceHandler
    intention_classifier: IntentionClassifier
    assistant: Assistant
    settings: Settings
