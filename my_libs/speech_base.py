from queue import Full, Queue
import sys
import json
import os
import string
import threading
import webrtcvad
from constants import MIC_SAMPLERATE, FRAME_DURATION
import numpy as np

class Speech_Base(object):
    
    def __init__(self, model):
        self.model = model
        self.q = Queue(maxsize=20)
        self.commands = self.get_commands()
        self.list_commands = self.get_list_of_commands()
        self.stop_evt = threading.Event()
        self.vad = webrtcvad.Vad(3)  #0 je najmenej agresivny 3 je najagresivny 
        self.noise_floor = 0.0
        self.noise_floor = 0.0
        self.noise_ready = False
        self.noise_init_blocks = 0
        self.noise_init_target = 30

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        try:
            self.q.put_nowait(bytes(indata))
        except Full:
            pass
        #self.q.put(indata)

    def get_commands(self):
        here = os.path.dirname(os.path.abspath(__file__))
        commands_path = os.path.join(here, "commands.json") 
        with open(commands_path, "r", encoding="utf-8") as file:
            commands = json.load(file)
            return commands
        
    def get_list_of_commands(self):
        commands_list = list(self.commands.keys())
        commands_list.append("[unk]")
        commands_json = json.dumps(commands_list)
        return commands_json

    def handle_command(self, text):
        text = (text or "").strip().lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        if not text:
            return -1
        
        for key, value in self.commands.items():
            if key == text:
                print(f"Command detected {key}, code {value}")
                return value
        
        print(f"Unknown command, heard - {text}")
        return -1

    def resample_soxr(self, input_block, in_rate, out_rate):
        pass

    def speech_read(self):
        pass

    def stop_stream(self):
        self.stop_evt.set()

    