import os
import pandas as pd
from datetime import datetime

def insert_to_csv(data, file):
    # Check if the file exists and is not empty
    if os.path.exists(file) and os.path.getsize(file) > 0:
        df = pd.read_csv(file)
    else:
        df = pd.DataFrame(columns=['groupName', 'students', 'date', 'sequence'])

    # Add new rows to the DataFrame
    df.loc[len(df)] = [data['groupName'] + '_template',
                       data['students'],
                       datetime.now().date().strftime('%Y-%m-%d'),
                       'CGAC' + data['codingStrand']]
    df.loc[len(df)] = [data['groupName'] + '_coding',
                       data['students'],
                       datetime.now().date().strftime('%Y-%m-%d'),
                       'CCGC' + get_complement(data['codingStrand'][::-1])]

    # Save the DataFrame back to the CSV file
    df.to_csv(file, index=False)

def get_complement(seq):
    toReturn = ''
    mapping = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    for char in seq:
        toReturn += mapping[char]
    return toReturn
