import os

import numpy as np
import torch
from torch.utils.data import DataLoader, SequentialSampler, TensorDataset
from tqdm import tqdm
from scipy.special import softmax
from src.utils import MODEL_CLASSES, get_intent_labels, get_slot_labels, load_tokenizer

def load_model(model_dir, args, device):
    # Check whether model exists
    if not os.path.exists(model_dir):
        raise Exception("Model doesn't exists! Train first!")

    try:
        model = MODEL_CLASSES[args.model_type][1].from_pretrained(
            args.model_dir, args=args, intent_label_lst=get_intent_labels(args), slot_label_lst=get_slot_labels(args)
        )
        model.to(device)
        model.eval()
        print("model loaded")
        # logger.info("***** Model Loaded *****")
    except Exception:
        raise Exception("Some model files might be missing...")

    return model



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

class IDSF():
    def __init__(self):
        self.model_dir = "./IDSF/model"
        self.args = torch.load(os.path.join(self.model_dir, "training_args.bin"))
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = load_model(self.model_dir,self.args,self.device)
        self.intent_label_lst = get_intent_labels(self.args)
        self.slot_label_lst = get_slot_labels(self.args)
        self.tokenizer = load_tokenizer(self.args)

    def read_input_file(self,input_file):
        lines = []
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                words = line.split()
                lines.append(words)

        return lines
    def predict(self,text):

        output_file = "out.txt"

        # Convert input file to TensorDataset
        pad_token_label_id = self.args.ignore_index
        lines = [text.split()]
        # lines = self.read_input_file('inp.txt')
        dataset = convert_input_to_tensor_dataset(lines,  self.args, self.tokenizer, pad_token_label_id)

        # Predict
        sampler = SequentialSampler(dataset)
        data_loader = DataLoader(dataset, sampler=sampler, batch_size=1)

        all_slot_label_mask = None
        intent_preds = None
        slot_preds = None
        with torch.no_grad():
            for batch in tqdm(data_loader, desc="Predicting"):
                batch = tuple(t.to(self.device) for t in batch)
                with torch.no_grad():
                    inputs = {
                        "input_ids": batch[0],
                        "attention_mask": batch[1],
                        "intent_label_ids": None,
                        "slot_labels_ids": None,
                    }
                    if self.args.model_type != "distilbert":
                        inputs["token_type_ids"] = batch[2]
                    outputs = self.model(**inputs)
                    _, (intent_logits, slot_logits) = outputs[:2]

                    # Intent Prediction
                    if intent_preds is None:
                        intent_preds = intent_logits.detach().cpu().numpy()
                    else:
                        intent_preds = np.append(intent_preds, intent_logits.detach().cpu().numpy(), axis=0)

                    # Slot prediction
                    if slot_preds is None:
                        slot_preds = slot_logits.detach().cpu().numpy()
                        all_slot_label_mask = batch[3].detach().cpu().numpy()
                    else:
                        slot_preds = np.append(slot_preds, slot_logits.detach().cpu().numpy(), axis=0)
                        all_slot_label_mask = np.append(all_slot_label_mask, batch[3].detach().cpu().numpy(), axis=0)

        print("og: \n",intent_preds)
        # intent_preds_softmax = softmax(intent_preds,axis = 1)
        # print("softmax: \n",intent_preds_softmax)

        slot_preds = np.argmax(slot_preds, axis=2)

        slot_label_map = {i: label for i, label in enumerate(self.slot_label_lst)}
        slot_preds_list = [[] for _ in range(slot_preds.shape[0])]

        for i in range(slot_preds.shape[0]):
            for j in range(slot_preds.shape[1]):
                if all_slot_label_mask[i, j] != pad_token_label_id:
                    slot_preds_list[i].append(slot_label_map[slot_preds[i][j]])

        for words, slot_preds, intent_pred in zip(lines, slot_preds_list, intent_preds):
                line = ""
                for word, pred in zip(words, slot_preds):
                    if pred == "O":
                        line = line + word + " "
                    else:
                        line = line + "[{}:{}] ".format(word, pred)
                # f.write("<{}> -> {}\n".format(self.intent_label_lst[intent_pred], line.strip()))

        intent_preds = scoreBoost(intent_preds,text,slot_preds)
        intent_preds_max = np.argmax(intent_preds, axis=1)

        print("after: \n",intent_preds,intent_preds_max)

        if intent_preds[0,intent_preds_max[0]] <= 10.5:
            intent_preds_max[0] = 0

        intent_preds = intent_preds_max
        
        # print(intent_preds)
        
       

        # Write to output file
        # with open(output_file, "a", encoding="utf-8") as f:
       
        return text,self.intent_label_lst[intent_preds[0]], slot_preds

def scoreBoost(arr,text, slot_preds):
    #Boost prediction score for higher classification accuracy
    songBoost = ['bài hát', 'bài nhạc', 'bài', 'ca khúc', 'phát', 'nhạc', 'giai điệu', 'tác phẩm', 'album','nghe' ,'bật','mở']
    alarmBoost = ['báo thức', 'lúc', 'sáng', 'chiều', 'tối', 'mỗi', 'dậy','lịch']
    timerBoost = ['hẹn giờ','sau','giờ','phút','giây','tiếng']
    weatherBoost = ['thời tiết','trời','nắng','mưa','dự báo','gió','nóng','ẩm']

    
    #for play_song
    if any(filter(lambda i: i in text,songBoost)):
        arr[0,1] = arr[0,1]+1.5
    #for timer
    elif any(filter(lambda i: i in text,timerBoost)):
        arr[0,2] = arr[0,2]+1.5
    #for alarm
    elif any(filter(lambda i: i in text,alarmBoost)):
        arr[0,3] = arr[0,3]+1.5
    #for weather
    elif any(filter(lambda i: i in text,weatherBoost)):
        arr[0,4] = arr[0,4]+1.5
    #no boost -> more likely to be unk
    else:
        for x in range(5):
            arr[0,x] = arr[0,x] - 2
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
