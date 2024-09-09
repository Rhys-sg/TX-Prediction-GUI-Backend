import numpy as np
import pandas as pd

def predict(seq, model):
    full_seq = get_full_seq(seq, model)
    encoded_seq = one_hot_encode(full_seq)
    prediction = model.predict(encoded_seq)[0][0]
    return float(prediction.item())

def get_full_seq(seq, model):
    insert = 'TTAATACTAGAGGTCTTCCGAC' + seq + 'GCGGGAAGACAACTAGGGGCCCA'
    input_len = model.input_shape[1]
    return '0' * (input_len - len(insert)) + insert

def one_hot_encode(sequence):
    mapping = {'A': [1,0,0,0], 'C': [0,1,0,0], 'G': [0,0,1,0], 'T': [0,0,0,1], '0': [0,0,0,0]}
    encoding = [mapping[nucleotide] for nucleotide in sequence]
    return np.array([encoding])