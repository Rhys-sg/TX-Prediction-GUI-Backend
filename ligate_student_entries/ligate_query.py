import os
import pandas as pd
import json

def query_from_csv(file):
    # Check if the file exists and is not empty
    if os.path.exists(file) and os.path.getsize(file) > 0:
        df = pd.read_csv(file)
    else:
        df = pd.DataFrame(columns=['groupName', 'students', 'date', 'sequence'])
        
    return df.to_dict(orient='records')
