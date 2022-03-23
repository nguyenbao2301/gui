
import time
from tokenize import Double
import numpy as np
import argparse
from sonopy import mfcc_spec
import os
import wave
import pyaudio
import noisereduce as nr
import soundfile as sf
import scipy
import dtw as DTW
from scipy.io import wavfile

from src.wakeword import Listener
# from python_speech_features import mfcc
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

stride = (400,200)
fft_size = 400
num_filt = 26
num_coeffs = 13
   

def dtw(x,y):
    #Input: Transposed mfccs (mfcc1.T and mfcc2.T)
    #output: DTW distance(unnormalized)
    len_x,len_y = len(x),len(y)
    cost_mtx = np.zeros((len_x+1,len_y+1))
    for i in range(len_x+1):
        for j in range(len_y+1):
            cost_mtx[i,j] = np.inf
    cost_mtx[0,0] = 0

    for i in range(1,len_x+1):
        for j in range(1,len_y+1):
            cost = abs(scipy.spatial.distance.cosine(x[i-1],y[j-1]))
            prev = np.min([cost_mtx[i-1,j],cost_mtx[i,j-1],cost_mtx[i-1,j-1]])
            cost_mtx[i,j]  = cost + prev

    return cost_mtx[len_x,len_y]    


def loadPatterns(path):
    dir = os.listdir(path)
    temp = []
    avg_len = 0
    for file in dir:
        # print(file)
        if  file.endswith('.wav'):
            wave,sr = sf.read(os.path.join(path,file),dtype="int16")
            # print(wave)
            wave = nr.reduce_noise(wave,sr=sr,n_fft=512,prop_decrease=0.2 )
            mfcc = mfcc_spec(wave,sr,stride,fft_size,num_filt,num_coeffs)
            # _mfcc = mfcc(wave,sr)
            avg_len += len(wave)
            # mfcc = librosa.feature.mfcc(wave,sr,n_mfcc=40,hop_length=int(0.010*sr), n_fft=int(0.025*sr))
            # print(wave,wave.shape )

            temp.append(mfcc)
    # print(avg_len/(len(dir)))
    return temp,(avg_len/(len(dir)))

def save( waveforms, fname="wakeword_temp.wav"):
        fname = os.path.join(config.get('main','temp_dir'),fname)
        wf = wave.open(fname, "wb")
        p = pyaudio.PyAudio()
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b"".join(waveforms))
        wf.close()
        return fname


def norm(i,mtx):
    return (len(mtx) - i)/len(mtx)
def calc(wave,sr,patterns,sensitivity):
    mfcc = mfcc_spec(wave,sr,stride,fft_size,num_filt,num_coeffs)
    # _mfcc = mfcc(wave,sr)
    for pattern in patterns:
        # dis = dtw(pattern,mfcc)
        dis = DTW.dtw(pattern,mfcc,distance_only=True,dist_method = "cosine")
        # print(dis.distance ,end = '\t')
        # print(dis.normalizedDistance*100,end= '\r')
        if dis.normalizedDistance*100 < sensitivity:
        # if dis.distance < sensitivity:
            return True
            # pass
    return False

def main(args):
    
    patterns,_ = loadPatterns(args.pattern_dir)
    wave,sr = sf.read(args.query,dtype="int16")
    res = calc(wave,sr,patterns,args.sensitivity)
    print("\n",res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pattern_dir', type=str)
    parser.add_argument('--noise_dir', type=str)
    parser.add_argument('--query', type=str)
    parser.add_argument('--sensitivity', type=float)
    args = parser.parse_args()
    main(args)


def DTWloop(func):
        print("testing")
        # print("s: ",sensitivity)
        listener = Listener()
        pattern_dir = config.get('main','pattern_dir')
        patterns,n = loadPatterns(pattern_dir)
        count = 0
        n= int(n/listener.chunk)
        frames = []
        while(True):
            res = 0
            config.read('config.ini')
            try:
                sensitivity = float(config.get('main','sensitivity'))  
            except Exception as e:
                continue
            # print(config.get('main','sensitivity'))
            data = listener.stream.read(listener.chunk, exception_on_overflow = False)
            frames.append(data)
            if len(frames)>= n:
                while len(frames)>n:
                    frames.pop(0)
                fname = listener.save_audio(frames)
                try:
                    sr,wave = wavfile.read(fname)
                    wave = nr.reduce_noise(wave,sr=sr,n_fft=512,prop_decrease=0.2 )
                    # print(wave.shape,end= "\r")
                    res = calc(wave,listener.sample_rate,patterns,sensitivity)
                except Exception as e:
                    continue
                finally: 
                    if res:
                        count+=1
                    else:
                        count = 0
                    if count > 8:
                        print("Yes. How can I help you?",sensitivity)
                        frames = []
                        count = 0
                        func()
                        time.sleep(0.5)
                    