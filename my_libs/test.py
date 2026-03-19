import whisper
from vosk import Model
from speech_factory import SpeechFactory

WHISPER = whisper.load_model("base.en")
VOSK_PATH = "/root/data/shared/sofiia_ws/src/voice_ctrl_sofiia/models/vosk-model-small-en-us-0.15"
VOSK = Model(VOSK_PATH)

#create factory
factory = SpeechFactory()

speech = factory.create_speech("whisper", WHISPER)

speech.speech_read()
