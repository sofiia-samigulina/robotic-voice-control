from speech_base import Speech_Base
import sounddevice as sd
from vosk import KaldiRecognizer
import json
import soxr
import numpy as np
from constants import MIC_SAMPLERATE, MODEL_SAMPLERATE, DEVICE, BLOCKSIZE
from queue import Empty
import time

class VoskSpeechGrammar(Speech_Base):

    def __init__(self, model):
        super().__init__(model)
        self.rec = None

    #resample 48k > 16k because Vosk wants 16k but microphone gives 48k
    def resample_soxr(self, input_block, in_rate, out_rate):
        # input_block — array of int16
        input_block = np.frombuffer(input_block, dtype=np.int16)
        output_block = soxr.resample(input_block, in_rate, out_rate)
        return output_block.astype(np.int16).tobytes()

    def speech_read(self):

        if self.rec is None:
            self.rec = KaldiRecognizer(self.model, MODEL_SAMPLERATE, self.list_commands)

        while not self.q.empty():
            try:
                self.q.get_nowait()
            except Empty:
                break

        with sd.RawInputStream(samplerate=MIC_SAMPLERATE, blocksize = BLOCKSIZE, device = DEVICE,
            dtype="int16", channels=1, callback=self.callback):
                    print("Start listening...")

                    while not self.stop_evt.is_set():
                        try:
                            data = self.q.get(timeout=0.1)
                        except Empty: continue
                        data_resampled = self.resample_soxr(data, MIC_SAMPLERATE, MODEL_SAMPLERATE)

                        if self.rec.AcceptWaveform(data_resampled):
                            start = time.time()
                            text = json.loads(self.rec.Result()).get("text", "")

                            if text == "":
                                 continue

                            output = self.handle_command(text)
                        
                            if output == -1:
                                continue
                        
                            end = time.time()
                            print(f"Time for recognition {end-start:.2f} sec")
                            
                            return output
                        
class VoskSpeechUsual(Speech_Base):
    def __init__(self, model):
        super().__init__(model)
        self.rec = None

    #resample 48k > 16k because Vosk wants 16k but microphone gives 48k
    def resample_soxr(self, input_block, in_rate, out_rate):
        # input_block — array of int16
        input_block = np.frombuffer(input_block, dtype=np.int16)
        output_block = soxr.resample(input_block, in_rate, out_rate)
        return output_block.astype(np.int16).tobytes()

    def speech_read(self):

        if self.rec is None:
            self.rec = KaldiRecognizer(self.model, MODEL_SAMPLERATE)

        while not self.q.empty():
            try:
                self.q.get_nowait()
            except Empty:
                break

        with sd.RawInputStream(samplerate=MIC_SAMPLERATE, blocksize = BLOCKSIZE, device = DEVICE,
            dtype="int16", channels=1, callback=self.callback):
                    print("Start listening...")

                    while not self.stop_evt.is_set():
                        try:
                            data = self.q.get(timeout=0.1)
                        except Empty: continue
                        data_resampled = self.resample_soxr(data, MIC_SAMPLERATE, MODEL_SAMPLERATE)

                        if self.rec.AcceptWaveform(data_resampled):
                            start = time.time()
                            text = json.loads(self.rec.Result()).get("text", "")

                            if text == "":
                                 continue

                            output = self.handle_command(text)
                        
                            if output == -1:
                                continue
                            
                            end = time.time()
                            print(f"Time for recognition {end-start:.2f} sec")
                            return output

 