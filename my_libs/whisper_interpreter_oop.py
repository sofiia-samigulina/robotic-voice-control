from speech_base import Speech_Base
import sounddevice as sd
import numpy as np
import soxr
from constants import MIC_SAMPLERATE, MODEL_SAMPLERATE, DEVICE, BLOCKSIZE, MIN_SAMPLES, FRAME_DURATION
from queue import Empty
from collections import deque

class WhisperSpeech(Speech_Base):

    #resample 48k > 16k because Whisper wants 16k but microphone gives 48k
    def resample_soxr(self, input_block, in_rate, out_rate):
        input_block = np.frombuffer(input_block, dtype=np.int16).astype(np.float32) / 32768.0
        output_block = soxr.resample(input_block, in_rate, out_rate)
        return output_block.astype(np.float32) 
    

    def get_rms(self, pcm_16bit):
        audio = np.frombuffer(pcm_16bit, dtype=np.int16).astype(np.float32) / 32768.0
        return float(np.sqrt(np.mean(audio ** 2)) + 1e-10)
    
    def update_noise_floor(self, rms, alpha=0.99): 
        if self.noise_floor == 0.0:
            self.noise_floor = rms
        else:
            self.noise_floor = alpha * self.noise_floor + (1-alpha) * rms

    def is_louder_than_background(self, rms, min_ratio=1.15, min_delta = 0.001):
        if self.noise_floor == 0.0:
            return rms > min_delta
        
        ratio = rms/self.noise_floor
        delta = rms - self.noise_floor

        return ratio >= min_ratio and delta >= min_delta

    def vad_has_speech(self, pcm_16bit, samplerate = MIC_SAMPLERATE, frame_duration_ms = FRAME_DURATION, threshold = 0.3):
        bytes_per_sample = 2 #because int16 16 bit is 2 byte
        frame_size = bytes_per_sample * int(samplerate * frame_duration_ms / 1000)
        if len(pcm_16bit) < frame_size:
            return False
        
        total_frames = 0
        speech_frames = 0

        for i in range(0, len(pcm_16bit) - frame_size + 1, frame_size):
            frame = pcm_16bit[i:i + frame_size]
            total_frames +=1
            if self.vad.is_speech(frame, samplerate):
                speech_frames += 1
        if total_frames == 0:
            return False
        return (speech_frames / total_frames) >= threshold
            
    def listen_speech(self): 
        raw_chunks = []
        silence_blocks = 0
        speech_started = False
        
        #pre istotu aby nestratit zaciatok vety
        pre_buffer_blocks = 8
        pre_buffer = deque(maxlen=pre_buffer_blocks)

        max_silence_blocks = 4  #test

        speech_confirm_blocks = 0
        min_speech_start_blocks = 4

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
                    block = self.q.get(timeout=0.1)
                except Empty: continue

                rms = self.get_rms(block)
                
                if not self.noise_ready:
                    vad_boot = self.vad_has_speech(
                        block,
                        samplerate=MIC_SAMPLERATE,
                        frame_duration_ms=FRAME_DURATION,
                        threshold=0.6
                    )

                    if not vad_boot:
                        self.update_noise_floor(rms)
                        self.noise_init_blocks += 1

                    if self.noise_init_blocks >= self.noise_init_target:
                        self.noise_ready = True
                        print(f"Noise floor initialized: {self.noise_floor:.4f}")

                    continue

                vad_ok = self.vad_has_speech(block, samplerate=MIC_SAMPLERATE, frame_duration_ms=FRAME_DURATION, threshold=0.6)
                loud_enough = self.is_louder_than_background(rms)
                has_speech = vad_ok and loud_enough

                if not speech_started:
                    pre_buffer.append(block)

                    if has_speech:
                        speech_confirm_blocks += 1
                    else: 
                        speech_confirm_blocks = 0
                        should_update_noise = False

                        if self.noise_floor == 0.0:
                            should_update_noise = True
                        elif (not vad_ok) and (rms <= self.noise_floor * 1.1):
                            should_update_noise = True

                        if should_update_noise:
                            self.update_noise_floor(rms)

                    if speech_confirm_blocks >= min_speech_start_blocks:
                        speech_started = True
                        silence_blocks = 0
                        raw_chunks.extend(pre_buffer)
                        pre_buffer.clear()

                    else:
                        continue

                else:
                    raw_chunks.append(block)
                    if has_speech:
                        silence_blocks = 0
                    else:
                        silence_blocks += 1
                current_raw_bytes = sum(len(c) for c in raw_chunks)
                current_raw_samples = current_raw_bytes // 2

                min_raw_samples = (MIN_SAMPLES * (MIC_SAMPLERATE / MODEL_SAMPLERATE))

                if speech_started and current_raw_samples > min_raw_samples and silence_blocks >= max_silence_blocks:
                    raw_audio = b"".join(raw_chunks)

                    raw_chunks = []
                    silence_blocks = 0
                    pre_buffer.clear()
                    speech_started = False

                    while not self.q.empty():
                        try:
                            self.q.get_nowait()
                        except Empty:
                            break

                    #resampling
                    audio_buffer = self.resample_soxr(raw_audio, MIC_SAMPLERATE, MODEL_SAMPLERATE)

                    segment_rms = float(np.sqrt(np.mean(audio_buffer ** 2)) + 1e-10)
                   
                    if segment_rms < max(self.noise_floor * 0.95, 0.005):
                        print("Rejected: segment too weak")
                        continue
                            
                    if len(audio_buffer) < MIN_SAMPLES:
                        print("Too short")
                        continue

                    return audio_buffer
        return None
                
    def speech_recognize(self, audio_buffer):
        print("Sent to transcribe, please wait")
        result = self.model.transcribe(
            audio_buffer,
            language="en",
            fp16=False,
            condition_on_previous_text=False,
            temperature =0,
            initial_prompt = (
                "Robot voice commands are: " +
                ", ".join(self.commands.keys()) +
                ". Output only one command.")
            )
        return result["text"]
    
    def speech_read(self):
        audio_buffer = self.listen_speech()
        if audio_buffer is None:
            return -1
        text = self.speech_recognize(audio_buffer)
        if text == "":
            return -1
        output = self.handle_command(text)                       
        return output
        
                    