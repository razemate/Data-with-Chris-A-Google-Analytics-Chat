import pandas as pd

def export_data(data):
    df = pd.DataFrame([{"Result": data}])
    df.to_csv("report.csv", index=False)
