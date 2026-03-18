import pandas as pd
from pathlib import Path

print("dataload.py loaded")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "Data"/"online_retail_II.xlsx"

def load_data():

    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Data file not found at {DATA_FILE}")
    
    return pd.read_excel(DATA_FILE)

if __name__ == "__main__":
    df = load_data()
    print(df.head())