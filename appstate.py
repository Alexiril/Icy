from assistant import Assistant
from intention_classifier import IntentionClassifier
from settings import Settings
from voice_handler import VoiceHandler


class AppState:

    voice_handler: VoiceHandler
    intention_classifier: IntentionClassifier
    assistant: Assistant
    settings: Settings
