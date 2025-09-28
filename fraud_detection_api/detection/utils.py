from .models import FraudPrediction
import pandas as pd
import numpy as np

def get_next_transaction_number():
    last = FraudPrediction.objects.order_by("id").last()
    if not last or not last.transaction_id:
        return 101
    try:
        return int(last.transaction_id.replace("txn", "")) + 1
    except ValueError:
        return 101
    
def clean_for_json(data: dict) -> dict:
    clean = {}
    for k, v in data.items():
        if isinstance(v, (np.generic,)):
            v = v.item()

        if pd.isna(v):
            v = None

        if isinstance(v, str):
            v = v.strip()

        clean[k] = v
    return clean