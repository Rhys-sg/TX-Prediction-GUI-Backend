import os

# Function to read and return the contents of a CSV file
def download_csv(filename):
    file_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'rb') as f:
            return f.read()
    else:
        raise FileNotFoundError(f"File '{filename}' not found or empty.")