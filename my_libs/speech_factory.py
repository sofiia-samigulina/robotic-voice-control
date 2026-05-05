from whisper_interpreter_oop import WhisperSpeech
from vosk_interpreter_oop import VoskSpeechGrammar, VoskSpeechUsual

class SpeechFactory(object):

    def create_speech(self, engine, model):
        engine_lower = engine.lower()
        if engine_lower == "whisper":
            return WhisperSpeech(model)
        elif engine_lower == "vosk":
            return VoskSpeechGrammar(model)
            #return VoskSpeechUsual(model)
        else:
            raise ValueError("Unknown speech engine")