from faster_whisper import WhisperModel
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from datetime import datetime, timedelta
import openai
from typing import Callable
import signal

from config.config_variables import api_credentials, enabled_features

openai.api_key = api_credentials["openai"]["key"]

# Original Code by Nik Stromberg - nikorasu85@gmail.com - MIT 2022 - copilot

class StreamHandler:
    def __init__(self, sample_rate = 16000, block_size=150, max_threshold=0.3, mean_threshold=0.1, end_blocks=10):
        self.running = True
        self.padding = 0
        self.prevblock = self.buffer = np.zeros((0,1))
        self.fileready = False

        self.SampleRate = sample_rate
        self.BlockSize = block_size
        self.Max_Threshold = max_threshold
        self.Mean_Threshold = mean_threshold
        self.EndBlocks = end_blocks

        self.start_transcription_time = None

        if enabled_features["self_host_whisper"]:
            self.model = WhisperModel("medium", device="cpu", compute_type="int8")

    def calibration_callback(self, indata, frames, time, status):
        if indata.max() > self.Max_Threshold:
            self.Max_Threshold = indata.max()
        if np.sqrt(np.mean(indata**2)) > self.Mean_Threshold:
            self.Mean_Threshold = np.sqrt(np.mean(indata**2))
        
        self.time -= 1            
        if self.time < 0:
            self.running = False

    def callback(self, indata:np.ndarray, frames, time, status):
        #zero_crossing_rate = np.sum(np.abs(np.diff(np.sign(indata)))) / (2 * indata.shape[0]) # threshold 20
        # freq = np.argmax(np.abs(np.fft.rfft(indata[:, 0]))) * SampleRate / frames

        if any(indata) and indata.max() > self.Max_Threshold and np.sqrt(np.mean(indata**2)) > (self.Mean_Threshold / 2):
            if self.padding < 1: 
                self.buffer = self.prevblock.copy()
                self.start_transcription_time = datetime.utcnow()
            self.buffer = np.concatenate((self.buffer, indata))
            self.padding = self.EndBlocks
        else:
            self.padding -= 1
            if self.padding > 1:
                self.buffer = np.concatenate((self.buffer, indata))
            elif self.padding < 1 < self.buffer.shape[0] > self.SampleRate: # if enough silence has passed, write to file.
                write('dictate.wav', self.SampleRate, self.buffer)
                self.fileready = True
                self.buffer = np.zeros((0,1))
            elif self.padding < 0 < self.buffer.shape[0] < self.SampleRate: # if recording not long enough, reset buffer.
                self.buffer = np.zeros((0,1))
            else:
                self.prevblock = indata.copy()

    def process(self):
        try:
            if self.fileready:
                with open("dictate.wav", "rb") as wav:
                    if enabled_features["self_host_whisper"]:
                        segments, info = self.model.transcribe("dictate.wav", beam_size=5, initial_prompt=self.prompt)

                        result = ""
                        for segment in segments:
                            result += segment.text
                    else:
                        result = openai.Audio.transcribe("whisper-1", wav, prompt=self.prompt)["text"]
                    
                    self.transcription_callback(result, self.start_transcription_time)
                    self.start_transcription_time = None
                    self.fileready = False
        except Exception as e:
            print(f"Error Transcribing: {e}")

    def listen(self, callback:Callable[[str, datetime], None], prompt:str=""):
        self.transcription_callback = callback
        self.prompt = prompt

        print("Listening...")
        with sd.InputStream(channels=1, callback=self.callback, blocksize=int(self.SampleRate * self.BlockSize / 1000), samplerate=self.SampleRate) as stream:
            while self.running: self.process()
            stream.close()
            self.running = True
    
    def calibrate(self, time=100):
        self.Max_Threshold = 0
        self.Mean_Threshold = 0

        self.time = time

        print("Calibrating...")
        with sd.InputStream(channels=1, callback=self.calibration_callback, blocksize=int(self.SampleRate * self.BlockSize / 1000), samplerate=self.SampleRate) as stream:
            while self.running: pass
            stream.close()
            self.running = True
            
            self.Max_Threshold *= 1.2
            self.Mean_Threshold *= 1.2

            print("Max: ", self.Max_Threshold)
            print("Avg: ", self.Mean_Threshold)