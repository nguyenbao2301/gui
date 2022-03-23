
from __future__ import unicode_literals

import argparse
import datetime   
import os
import time
import pyaudio
import wave
from src.utils import Audio


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 2.5
SNR_TRIM = 18
FOLDER_BASE = ""
MAX_RECORD_DURATION = 2
MAX_DIFFERENCE_DURATION = 0.3
DATE_FORMAT = '%Y_%m_%dT%H_%M_%S'


def record_one(directory, i):
    dest_path = os.path.join(directory, "{0}.wav".format(i))
    
    audio = pyaudio.PyAudio()

    print(
        """\n\nPress enter to record one sample, say your hotword when "recording..." shows up""")
    time.sleep(0.2)

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("recording...")
    frames = []

    for j in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("finished recording\n")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(dest_path, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(2)
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()


def check_audios(durations):
    if any([d > MAX_RECORD_DURATION for d in durations]):
        print("WARNING: at least one your record seems to have a too long " \
              "duration, you are going to have")

def validate(i,queue):
    directory = "temp"
    dest_path = os.path.join(directory, "{0}.wav".format(i))
    audio = Audio.from_file(dest_path)
    audio.trim_silences(SNR_TRIM)
    if audio.duration() > MAX_RECORD_DURATION:
        print("WARNING: there seems to be too much noise in your" \
                      " environment please retry to record this sample by " \
                      "following the instructions.")
        return 2
    if any([abs(audio_1.duration() - audio_2.duration()) > MAX_DIFFERENCE_DURATION for i, audio_1 in enumerate(queue) for j, audio_2 in enumerate(queue) if i < j]):
        print("WARNING: there seems to be too much difference between " \
                  "your records please retry to record all of them by following " \
                  "the instructions.")
        return 1

    queue.append(audio)
    return 0
    
def record_and_trim(hotword_key, nb_records=3):
    print("Your will have to record your personal hotword." \
              " Please be sure to be in a quiet environment." \
              " Press enter once you are ready.\n".format(
        nb_records))

    directory = os.path.join(FOLDER_BASE, "personal_{0}".format(str(datetime.datetime.now().strftime(DATE_FORMAT))))
    os.makedirs(directory)

    is_validated = False
    while not is_validated:
        audios = []
        for i in range(nb_records):
            record_one(directory, i)
            dest_path = os.path.join(directory, "{0}.wav".format(i))
            audio = Audio.from_file(dest_path)
            audio.trim_silences(SNR_TRIM)
            while audio.duration() > MAX_RECORD_DURATION:
                print("WARNING: there seems to be too much noise in your" \
                      " environment please retry to record this sample by " \
                      "following the instructions.")
                record_one(directory, i)
                audio = Audio.from_file(dest_path)
                audio.trim_silences(SNR_TRIM)
            audios.append(audio)

        if any([abs(
                        audio_1.duration() - audio_2.duration()) > MAX_DIFFERENCE_DURATION
                for i, audio_1 in enumerate(audios) for j, audio_2 in
                enumerate(audios) if i < j]):
            print("WARNING: there seems to be too much difference between " \
                  "your records please retry to record all of them by following " \
                  "the instructions.")
            audios = []
        else:
            is_validated = True

    for i, audio in enumerate(audios):
        dest_path = os.path.join(directory, "{0}.wav".format(i))
        audio.write(dest_path)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--hotword_key', type=str,
                        help="the name of your personal hotword (no special characters)")
    args = parser.parse_args()
    record_and_trim(args.hotword_key)
