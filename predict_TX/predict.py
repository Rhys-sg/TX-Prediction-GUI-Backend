import numpy as np
import pandas as pd

def predict(seq, model):
    full_seq = get_full_seq(seq)
    encoded_seq = one_hot_encode(full_seq)
    prediction = model.predict(encoded_seq)[0][0]
    return float(prediction.item())

def get_full_seq(seq):
    return 'TTAATACTAGAGGTCTTCCGAC' + seq[0:6] + '0' + seq[6:] + 'GCGGGAAGACAACTAGGGGCCCA'

def one_hot_encode(sequence):
    mapping = {'A': [1,0,0,0], 'C': [0,1,0,0], 'G': [0,0,1,0], 'T': [0,0,0,1], '0': [0,0,0,0]}
    encoding = [mapping[nucleotide] for nucleotide in sequence]
    return np.array([encoding])