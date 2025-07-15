import pandas as pd
from fredapi import Fred
from datetime import datetime

fred = Fred(api_key='2e6ed76af675c00fdc9c54bc66bbd234')

def fetch_series(series_id: str, start: str = "2000-01-01") -> pd.DataFrame:
    data = fred.get_series(series_id, observation_start=start)
    df = pd.DataFrame(data, columns=[series_id])
    df.index = pd.to_datetime(df.index)
    return df