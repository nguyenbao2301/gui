from cmath import exp
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
import time
import threading 
import ctypes
import torch
from torch.utils.data import DataLoader, SequentialSampler, TensorDataset

class AudioThread(threading.Thread):
    def __init__(self,file,volume):
        threading.Thread.__init__(self)
        self.file = file
        self.vol = volume
    def run(self):
        try:
            self.a = AudioPlayer(self.file)
            self.a.volume = int(self.vol)
            self.a.play(loop=True)
            while(True):
                continue
        finally:
            self.a.stop()
            self.a.close()
            print('ended')

    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
  
    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            # print('Exception raise failure')

def PlaySound(file,volume,_block=True):
    try:
        volume = int(volume)
        a = AudioPlayer(file)
        a.volume = volume
        a.play(block=_block)
    except Exception:
        print("audio error")

def PlayAlarm(file,volume):
    try:
        volume = int(volume)
        a = AudioPlayer(file)
        a.volume = volume
        a.play(loop=True)
        time.sleep(1)
        a.pause()
        return a
    except Exception:
        print("audio alarm error")
        return None
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

def scoreBoost(arr,text, slot_preds):
    #Boost prediction score for higher classification accuracy
    songBoost = ['bài hát', 'bài nhạc', 'bài', 'ca khúc', 'phát', 'nhạc', 'giai điệu', 'tác phẩm', 'album','nghe' ,'bật','mở']
    alarmBoost = ['báo thức', 'lúc', 'sáng', 'chiều', 'tối', 'mỗi', 'dậy','lịch','báo','gọi']
    timerBoost = ['hẹn giờ','sau','giờ','phút','giây','tiếng']
    weatherBoost = ['thời tiết','trời','nắng','mưa','dự báo','gió','nóng','ẩm']

    flag = []
    #for play_song
    if any([i in text for i in songBoost]):
        arr[0,1] = arr[0,1]+1.5
        flag.append(1)
        print('songBoost')
    #for timer
    if any([i in text for i in timerBoost]):
        arr[0,2] = arr[0,2]+1.5
        flag.append(2)
        print('timerBoost')
    #for alarm
    if any([i in text for i in alarmBoost]):
        arr[0,3] = arr[0,3]+1.5
        flag.append(3)
        print('alarmBoost')
    #for weather
    if any([i in text for i in weatherBoost]):
        arr[0,4] = arr[0,4]+1.5
        flag.append(4)
        print('weatherBoost')


    #no boost -> more likely to be unk
    print('flags: ',flag)
    for x in range(5):
            if x not in flag:
                arr[0,x] = arr[0,x] - 2
    print('no boost')
        
    imax = np.argmax(arr, axis=1) if arr[0,np.argmax(arr, axis=1)]>=10.0 else 0
    print("max:",imax,arr)
    for slot in slot_preds:
        if slot == "O" or "I" in slot:
            continue
        key =  slot[2:] 
        if key in ['song_name','artist','album','genre']:
            arr[0,1] = arr[0,1]+1
            for x in range(5):
                if imax==1:
                    arr[0,x]  = arr[0,x]-0.5 
                elif x != 1:
                    arr[0,x]  = arr[0,x]-1
                
        if key in ['hour','minute','second']:
            arr[0,2] = arr[0,2]+1
            for x in range(5):
                if imax==2:
                    arr[0,x]  = arr[0,x]-0.5 
                elif x!=2: 
                    arr[0,x]  = arr[0,x]-1
        if key in ['repeat']:
            arr[0,3] = arr[0,3]+1
            for x in range(5):
                if imax==3:
                    arr[0,x]  = arr[0,x]-0.5 
                elif x!=3:
                    arr[0,x]  = arr[0,x]-1
        if key in ['time']:
            arr[0,2] = arr[0,2]+1
            arr[0,3] = arr[0,3]+2
            for x in range(5):
                if imax==3 or imax ==2:
                    arr[0,x]  = arr[0,x]-0.5 
                elif x!= 2 and x!=3:
                    arr[0,x]  = arr[0,x]-1

        if key in ['pod','relative','date_name','date_number','month']:
            arr[0,3] = arr[0,3]+1
            arr[0,4] = arr[0,4]+0.5
            for x in range(5):
                if imax==4 or imax == 3:
                    arr[0,x]  = arr[0,x]-0.5 
                elif x!=3 and x!=4:
                    arr[0,x]  = arr[0,x]-1 
        if key in ['weather','location']:
            arr[0,4] = arr[0,4]+1
            for x in range(5):
                if imax==4:
                    arr[0,x]  = arr[0,x]-0.5 
                elif x!=4:
                    arr[0,x]  = arr[0,x]-1 
    return arr

    
def convert_input_to_tensor_dataset(
    lines,
    args,
    tokenizer,
    pad_token_label_id,
    cls_token_segment_id=0,
    pad_token_segment_id=0,
    sequence_a_segment_id=0,
    mask_padding_with_zero=True,
):
    # Setting based on the current model type
    cls_token = tokenizer.cls_token
    sep_token = tokenizer.sep_token
    unk_token = tokenizer.unk_token
    pad_token_id = tokenizer.pad_token_id

    all_input_ids = []
    all_attention_mask = []
    all_token_type_ids = []
    all_slot_label_mask = []

    for words in lines:
        tokens = []
        slot_label_mask = []
        for word in words:
            word_tokens = tokenizer.tokenize(word)
            if not word_tokens:
                word_tokens = [unk_token]  # For handling the bad-encoded word
            tokens.extend(word_tokens)
            # Use the real label id for the first token of the word, and padding ids for the remaining tokens
            slot_label_mask.extend([pad_token_label_id + 1] + [pad_token_label_id] * (len(word_tokens) - 1))

        # Account for [CLS] and [SEP]
        special_tokens_count = 2
        if len(tokens) > args.max_seq_len - special_tokens_count:
            tokens = tokens[: (args.max_seq_len - special_tokens_count)]
            slot_label_mask = slot_label_mask[: (args.max_seq_len - special_tokens_count)]

        # Add [SEP] token
        tokens += [sep_token]
        token_type_ids = [sequence_a_segment_id] * len(tokens)
        slot_label_mask += [pad_token_label_id]

        # Add [CLS] token
        tokens = [cls_token] + tokens
        token_type_ids = [cls_token_segment_id] + token_type_ids
        slot_label_mask = [pad_token_label_id] + slot_label_mask

        input_ids = tokenizer.convert_tokens_to_ids(tokens)

        # The mask has 1 for real tokens and 0 for padding tokens. Only real tokens are attended to.
        attention_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)

        # Zero-pad up to the sequence length.
        padding_length = args.max_seq_len - len(input_ids)
        input_ids = input_ids + ([pad_token_id] * padding_length)
        attention_mask = attention_mask + ([0 if mask_padding_with_zero else 1] * padding_length)
        token_type_ids = token_type_ids + ([pad_token_segment_id] * padding_length)
        slot_label_mask = slot_label_mask + ([pad_token_label_id] * padding_length)

        all_input_ids.append(input_ids)
        all_attention_mask.append(attention_mask)
        all_token_type_ids.append(token_type_ids)
        all_slot_label_mask.append(slot_label_mask)

    # Change to Tensor
    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long)
    all_attention_mask = torch.tensor(all_attention_mask, dtype=torch.long)
    all_token_type_ids = torch.tensor(all_token_type_ids, dtype=torch.long)
    all_slot_label_mask = torch.tensor(all_slot_label_mask, dtype=torch.long)

    dataset = TensorDataset(all_input_ids, all_attention_mask, all_token_type_ids, all_slot_label_mask)

    return dataset