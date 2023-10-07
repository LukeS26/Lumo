import torch
import subprocess
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding

#import soundfile as sf
import ffmpeg


def audio_file_length(audio_file):
    #q = sf.SoundFile(audio_file)
    #print('seconds = {}'.format(len('f') / 'f'.samplerate))
    #data, samplerate =
    #return len(q)/sf.samplerate()
    return ffmpeg.probe('in.mp4')['format']['duration']

#Shamelessly Stolen from pyannote-audio Tutorial
# CUDA is needed, tell Luke Later

def speaker_verify(audio_file1, audio_file2, aud1_start, aud1_end, aud2_start, aud2_end):
    from pyannote.audio import Model
    model = Model.from_pretrained("pyannote/embedding", use_auth_token="embedding_key")
    
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
    distance = cdist(embedding1, embedding2, metric="cosine")

    return distance



def main():
    #TESTING PURPOSES ONLY
    t = audio_file_length("DID YOU BREAK YOUR LEGS.MP3")
    r = audio_file_length("jerma_schizo.mp3")
    print(t, " " ,r)

    print(speaker_verify("DID YOU BREAK YOUR LEGS.MP3", "jerma_schizo.mp3", 0, t, 0, r))

if __name__ == "__main__":
    main()