from transcribe import StreamHandler;

import os
from config_variables.py import max_users

from mutagen.wave import WAVE
import numpy as np

from scipy.io.wavfile import write


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

def main():
   create_voice_profile()

if __name__ == "__main__":
    main()
