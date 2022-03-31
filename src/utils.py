from PIL import ImageEnhance
import tkinter as tk
from tkinter import filedialog,messagebox
import os
from model import JointPhoBERT
from transformers import (
    AutoTokenizer,
    RobertaConfig,
)
import logging
import numpy as np
import soundfile as sf
from audioplayer import AudioPlayer


def PlaySound(file,volume):
    volume = int(volume)
    a = AudioPlayer(file)
    a.volume = volume
    a.play(block=True)

def reduceOpacity(img,opacity):
    if hasattr(img,"mode") and img.mode != 'RGBA':
        i = img.convert('RGBA')
    else:
        i = img.copy()
    alpha = i.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    i.putalpha(alpha)
    return i

def browse(callback,init):
    filename = filedialog.askdirectory(initialdir=init)
    filename = os.path.normpath(filename)
    print(filename)
    callback(curDir = filename)

def clearDir(directory):
    if  messagebox.askyesno("Confirmation","Clear all keywords?\nYou will have to record new ones."):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e)) 
def restartThread():
    messagebox.showinfo(message= "This change will take effect after a program restart.")


MODEL_CLASSES = {
    "phobert": (RobertaConfig, JointPhoBERT, AutoTokenizer),
}


def get_intent_labels(args):
    return [
        label.strip()
        for label in open(os.path.join(args.data_dir, args.token_level, args.intent_label_file), "r", encoding="utf-8")
    ]


def get_slot_labels(args):
    return [
        label.strip()
        for label in open(os.path.join(args.data_dir, args.token_level, args.slot_label_file), "r", encoding="utf-8")
    ]


def load_tokenizer(args):
    return MODEL_CLASSES[args.model_type][2].from_pretrained(args.model_name_or_path,local_files_only = True)


def init_logger():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO,
    )

class Audio(object):
    def __init__(self, data, sample_rate):
        if data is not None:
            self.data = data
            if len(self.data.shape) == 1:
                self.data = self.data[:, np.newaxis]
            self.sample_rate = sample_rate
        else:
            self.data, self.sample_rate = None, None

    @classmethod
    def from_file(cls, filename):
        data, sample_rate = sf.read(filename)
        return cls(data, sample_rate)

    def trim_silences(self, threshold_db):
        self.data = np.expand_dims(
            trim(np.squeeze(self.data), top_db=threshold_db)[0], axis=1)

    def write(self, filename):
        sf.write(filename, self.data, self.sample_rate)

    def duration(self):
        return float(len(self.data)) / float(self.sample_rate)


def power_to_db(S, amin=1e-10):
    magnitude = np.abs(S)
    ref_value = np.max(magnitude)

    log_spec = 10.0 * np.log10(np.maximum(amin, magnitude))
    log_spec -= 10.0 * np.log10(np.maximum(amin, ref_value))

    return log_spec


class ViewArray(object):
    def __init__(self, interface, base):
        self.__array_interface__ = interface
        self.base = base


def as_strided(x, shape=None, strides=None):
    x = np.array(x, copy=False)
    interface = dict(x.__array_interface__)
    if shape is not None:
        interface['shape'] = tuple(shape)
    if strides is not None:
        interface['strides'] = tuple(strides)

    array = np.asarray(ViewArray(interface, base=x))
    array.dtype = x.dtype

    return array


def frame(y, frame_length=2048, hop_length=512):
    n_frames = 1 + int((len(y) - frame_length) / hop_length)
    y_frames = as_strided(y, shape=(frame_length, n_frames),
                          strides=(y.itemsize, hop_length * y.itemsize))
    return y_frames


def rmse(y, frame_length=2048, hop_length=512):
    y = np.pad(y, int(frame_length // 2), mode='reflect')
    x = frame(y, frame_length=frame_length, hop_length=hop_length)
    return np.sqrt(np.mean(np.abs(x) ** 2, axis=0, keepdims=True))


def _signal_to_frame_nonsilent(y, frame_length=2048, hop_length=512, top_db=60):
    mse = rmse(y=y,
               frame_length=frame_length,
               hop_length=hop_length) ** 2
    return power_to_db(mse.squeeze()) > - top_db


def frames_to_samples(frames, hop_length=512, n_fft=None):
    return (np.atleast_1d(frames) * hop_length).astype(int)


def trim(y, top_db=25, frame_length=2048, hop_length=512):
    non_silent = _signal_to_frame_nonsilent(y,
                                            frame_length=frame_length,
                                            hop_length=hop_length,
                                            top_db=top_db)
    nonzero = np.flatnonzero(non_silent)

    start = int(frames_to_samples(nonzero[0], hop_length))
    end = min(y.shape[-1],
              int(frames_to_samples(nonzero[-1] + 1, hop_length)))

    full_index = [slice(None)] * y.ndim
    full_index[-1] = slice(start, end)

    return y[tuple(full_index)], np.asarray([start, end])
