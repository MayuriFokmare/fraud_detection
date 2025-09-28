import pandas as pd
import logging

def engineer(df: pd.DataFrame) -> pd.DataFrame:
    if "Transaction Date" in df.columns:
        ts = pd.to_datetime(df["Transaction Date"], errors="coerce")
        df["trans_hour"] = ts.dt.hour
        df["trans_dow"] = ts.dt.dayofweek
    logging.info("Feature engineering complete. Shape: %s", df.shape)
    return df