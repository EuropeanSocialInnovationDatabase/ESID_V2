import html
import json
import os
import re

import torch
import unicodedata
from nltk.tokenize import sent_tokenize


# determine the supported device
def get_device():
    if torch.cuda.is_available():
        device = torch.device('cuda:0')
    else:
        device = torch.device('cpu')  # don't have GPU
    return device


# convert a df to tensor to be used in pytorch
def df_to_tensor(df):
    device = get_device()
    return torch.from_numpy(df.labels.values).float().to(device)


def get_list_of_dict(keys, list_of_tuples):
    """
    This function will accept keys and list_of_tuples as args and return list of dicts
    """
    list_of_dict = [dict(zip(keys, values)) for values in list_of_tuples]
    return list_of_dict


def clean_text(raw_text):
    def is_pua(c):
        return unicodedata.category(c) == 'Co'

    if not isinstance(raw_text, str):
        return ''

    try:
        clean_text = html.unescape(raw_text)
    except:
        clean_text = raw_text
    clean_text = clean_text.replace('\xa0', ' ').replace('\r', ' ').replace('&quot', ' ').replace('#', '').replace(
        '=', '')
    clean_text = re.sub(r'(\{|\<|\[)(.*)(\>|\]|\})', '', clean_text)  # text between [], (), {}
    clean_text = re.sub(r'\b\w{20,}\b', '', clean_text)  # long text
    sentences = sent_tokenize(clean_text)
    new_sents = []

    # remove dup sent:
    for sent in sentences:
        if sent not in new_sents:
            new_sents.append(sent)
    if new_sents:
        sentences = new_sents
    clean_text = ' '.join(sentences)
    clean_text = [x for x in clean_text.split('\n') if len(x.split()) > 2]
    clean_text = ' '.join(clean_text)
    clean_text = re.sub('\n', ' ', clean_text)
    clean_text = clean_text.replace('\n', '. ').replace('\t', '')

    clean_text = "".join([char for char in clean_text if not is_pua(char)])

    return clean_text


def write2file(filename, data):
    with open(filename, 'w', encoding='utf-8', errors='ignore') as wrt:
        wrt.write(data)


def load_json(json_path):
    if os.path.exists(json_path):
        with open(json_path, 'r') as rdr:
            data = json.load(rdr)
        return data
    else:
        return {}
