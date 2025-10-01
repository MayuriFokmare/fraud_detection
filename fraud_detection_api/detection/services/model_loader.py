import os
import joblib
from django.conf import settings

ML_BASE_DIR = os.path.abspath(os.path.join(settings.BASE_DIR, "..", "experiments"))

def load_model(fraud_type: str, model_name: str):
    model_path = os.path.join(
        ML_BASE_DIR,
        fraud_type,
        "models",
        f"{model_name}.joblib"
    )

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    return joblib.load(model_path)
