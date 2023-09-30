import torch
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding

#Shamelessly Stolen from pyannote-audio Tutorial

def speaker_verify(audio_file1, audio_file2, aud1_start, aud1_end, aud2_start, aud2_end):
    model = PretrainedSpeakerEmbedding(
        "speechbrain/spkrec-ecapa-voxceleb",
        device=torch.device("cuda"))

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

