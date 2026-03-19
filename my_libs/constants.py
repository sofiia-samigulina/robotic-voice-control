import sounddevice as sd

devs = sd.query_devices()
mic_index = next(i for i,d in enumerate(devs) if "USB Microphone" in d["name"] and d["max_input_channels"] > 0)

MIC_SAMPLERATE = 48000
MODEL_SAMPLERATE = 16000
DEVICE = mic_index
BLOCKSIZE = int(MIC_SAMPLERATE * 0.02)
MIN_SAMPLES = int(MODEL_SAMPLERATE * 0.7)
COMMANDS = 'commands.json'
FRAME_DURATION = 20
