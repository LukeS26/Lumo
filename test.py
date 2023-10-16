import torch
import subprocess
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
import config.config_variables as cv

import mutagen 
from mutagen.wave import WAVE 
#from mutagen.mp3 import MP3

def audio_file_length(audio_file):
    audio = WAVE(audio_file) 
    audio_info = audio.info 
    length = int(audio_info.length) 
    return length
#Shamelessly Stolen from pyannote-audio Tutorial
# CUDA is needed, tell Luke Later

""""
def speaker_verify(audio_file1, audio_file2, aud1_start, aud1_end, aud2_start, aud2_end):
    from pyannote.audio import Model
    model = Model.from_pretrained("pyannote/embedding", use_auth_token=cv.api_credentials["hugging_face"]["embedding_key"])
    
    from pyannote.audio import Audio
    from pyannote.core import Segment
    audio = Audio(sample_rate=16000, mono="downmix")

    # extract embedding for a speaker speaking between t=3s and t=6s
    speaker1 = Segment(aud1_start, aud1_end)
    waveform1, sample_rate = audio.crop(audio_file1, speaker1)
    embedding1 = model(waveform1[None])

    # extract embedding for a speaker speaking between t=7s and t=12s
    speaker2 = Segment(aud2_start, aud2_end)
    waveform2, sample_rate = audio.crop(audio_file2, speaker2)
    embedding2 = model(waveform2[None])

    # compare embeddings using "cosine" distance
    from scipy.spatial.distance import cdist
    distance = cdist(embedding1, embedding2, 'cosine')

    return distance
"""

def speaker_verify_2_0(filepath_1, filepath_2):
    import random

    import numpy as np

    from deep_speaker.audio import read_mfcc
    from deep_speaker.batcher import sample_from_mfcc
    from deep_speaker.constants import SAMPLE_RATE, NUM_FRAMES
    from deep_speaker.conv_models import DeepSpeakerModel
    from deep_speaker.test import batch_cosine_similarity

    # Reproducible results.
    np.random.seed(123)
    random.seed(123)

    model2 = DeepSpeakerModel()

    model2.m.load_weights('ResCNN_triplet_training_checkpoint_265.h5', by_name=True)

    mfcc_001 = sample_from_mfcc(read_mfcc(filepath_1, SAMPLE_RATE), NUM_FRAMES)
    mfcc_002 = sample_from_mfcc(read_mfcc(filepath_2, SAMPLE_RATE), NUM_FRAMES)

    predict_001 = model2.m.predict(np.expand_dims(mfcc_001, axis=0))
    predict_002 = model2.m.predict(np.expand_dims(mfcc_002, axis=0))

    return batch_cosine_similarity(predict_001, predict_002)



def main():
    #TESTING PURPOSES ONLY
    t = audio_file_length("DID YOU BREAK YOUR LEGS.wav")
    r = audio_file_length("jerma_schizo.wav")
    print(t, " " ,r)

    print(speaker_verify_2_0("./DID YOU BREAK YOUR LEGS.wav", "./jerma_schizo.wav"))

if __name__ == "__main__":
    main()