import pandas as pd

def parse_xlsx(filepath):
    df = pd.read_excel(filepath)
    return df.to_dict(orient='records')
