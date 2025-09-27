import pandas as pd


def generate_summary(fraud_type: str, model_name: str, df: pd.DataFrame) -> dict:
    """
    Returns high-level summary stats.
    """
    return {
        "fraud_type": fraud_type,
        "model_used": model_name,
        "total_records": len(df),
        "fraudulent_cases": int(df['fraud_prediction'].sum()),
        "fraud_rate": round(float(df['fraud_prediction'].mean()), 3),
    }


def generate_breakdown(fraud_type: str, df: pd.DataFrame) -> dict:
    """
    Returns breakdown counts for fraud vs non-fraud.
    """
    counts = df['fraud_prediction'].value_counts().to_dict()
    return {
        "fraud_type": fraud_type,
        "breakdown": {
            "non_fraud": int(counts.get(0, 0)),
            "fraud": int(counts.get(1, 0)),
        }
    }


def generate_probabilities(df: pd.DataFrame) -> dict:
    """
    Returns fraud probability distribution (basic).
    """
    avg_prob = float(df['fraud_probability'].mean())
    max_prob = float(df['fraud_probability'].max())
    min_prob = float(df['fraud_probability'].min())

    return {
        "probability_distribution": {
            "average_probability": round(avg_prob, 3),
            "max_probability": round(max_prob, 3),
            "min_probability": round(min_prob, 3),
        }
    }