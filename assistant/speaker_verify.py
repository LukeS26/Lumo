from transcribe import StreamHandler;

import random
import os
from config_variables.py import max_users

from mutagen.wave import WAVE
import numpy as np

from scipy.io.wavfile import write

from deep_speaker.audio import read_mfcc
from deep_speaker.batcher import sample_from_mfcc
from deep_speaker.constants import SAMPLE_RATE, NUM_FRAMES
from deep_speaker.conv_models import DeepSpeakerModel
from deep_speaker.test import batch_cosine_similarity

def audio_file_length(audio_file):
    audio = WAVE(audio_file) 
    audio_info = audio.info 
    length = int(audio_info.length) 
    return length

def speaker_verify(filepath_1, filepath_2):
    np.random.seed(123)
    random.seed(123)

    model2 = DeepSpeakerModel()

    model2.m.load_weights('../ResCNN_triplet_training_checkpoint_265.h5', by_name=True)

    mfcc_001 = sample_from_mfcc(read_mfcc(filepath_1, SAMPLE_RATE), NUM_FRAMES)
    mfcc_002 = sample_from_mfcc(read_mfcc(filepath_2, SAMPLE_RATE), NUM_FRAMES)

    predict_001 = model2.m.predict(np.expand_dims(mfcc_001, axis=0))
    predict_002 = model2.m.predict(np.expand_dims(mfcc_002, axis=0))

    return batch_cosine_similarity(predict_001, predict_002)

"""
def create_voice_profile():
    num = 0
    path = "../saved_voices"
    directory_list = os.listdir()

    for i in directory_list:
        if ".wav" in i:
            num += 1

    if num >= max_users:
        num = 0

    file_name = "Saved_voice_" + num + ".wav"
    
    StreamHandler().record(file_name)
    
    os.rename("./" + file_name, path + file_name)
"""