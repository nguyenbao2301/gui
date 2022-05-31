import os

import numpy as np
import torch
from torch.utils.data import DataLoader, SequentialSampler
from tqdm import tqdm
from src.utils import MODEL_CLASSES, get_intent_labels, get_slot_labels, load_tokenizer, scoreBoost, convert_input_to_tensor_dataset

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









