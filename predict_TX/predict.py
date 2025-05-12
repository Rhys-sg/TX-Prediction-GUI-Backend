import numpy as np
import pandas as pd

def predict(seq, model):
    # Calculated using linear regression between predicted values and log(relative fluorescence) values
    slope = 2.015845699353661
    intercept = 5.290007180011913

    full_seq = get_full_seq(seq, model)
    encoded_seq = one_hot_encode(full_seq)
    prediction = model.predict(encoded_seq)[0][0]

    log_Rel_RFP = slope * prediction + intercept
    Rel_RFP = int(10 ** log_Rel_RFP)

    return max(Rel_RFP, 50001)

def get_full_seq(seq, model):
    insert = 'AATACTAGAGGTCTTCCGAC' + seq + 'GCGGGAAGACAACTAGGGG'
    input_len = model.input_shape[1]
    return insert.zfill(input_len)

def one_hot_encode(sequence):
    mapping = {'A': [1,0,0,0], 'C': [0,1,0,0], 'G': [0,0,1,0], 'T': [0,0,0,1], '0': [0,0,0,0]}
    encoding = [mapping[nucleotide] for nucleotide in sequence]
    return np.array([encoding])