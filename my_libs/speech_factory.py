from whisper_interpreter_oop import WhisperSpeech
from vosk_interpreter_oop import VoskSpeech

class SpeechFactory(object):

    def create_speech(self, engine, model):
        engine_lower = engine.lower()
        if engine_lower == "whisper":
            return WhisperSpeech(model)
        elif engine_lower == "vosk":
            return VoskSpeech(model)
        else:
            raise ValueError("Unknown speech engine")