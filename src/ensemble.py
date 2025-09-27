import os, logging
import numpy as np
import pandas as pd
from scipy.stats import mode
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def run_ensembles(models: dict, X_test, y_test, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)

    # Collect predictions & probabilities
    preds = []
    probas = []
    for model in models.values():
        preds.append(model.predict(X_test))
        probas.append(model.predict_proba(X_test)[:, 1])

    preds = np.vstack(preds)   # shape: (n_models, n_samples)
    probas = np.vstack(probas) # shape: (n_models, n_samples)

    # 🔹 Hard voting (majority)
    y_pred_majority = mode(preds, axis=0, keepdims=True).mode.flatten()

    # 🔹 Soft voting (average probabilities)
    y_proba_avg = np.mean(probas, axis=0)
    y_pred_soft = (y_proba_avg >= 0.5).astype(int)

    # 🔹 Metrics
    results = {
        "majority_vote": {
            "accuracy": accuracy_score(y_test, y_pred_majority),
            "precision": precision_score(y_test, y_pred_majority, zero_division=0),
            "recall": recall_score(y_test, y_pred_majority, zero_division=0),
            "f1": f1_score(y_test, y_pred_majority, zero_division=0),
            "roc_auc": roc_auc_score(y_test, y_pred_majority)
        },
        "soft_vote": {
            "accuracy": accuracy_score(y_test, y_pred_soft),
            "precision": precision_score(y_test, y_pred_soft, zero_division=0),
            "recall": recall_score(y_test, y_pred_soft, zero_division=0),
            "f1": f1_score(y_test, y_pred_soft, zero_division=0),
            "roc_auc": roc_auc_score(y_test, y_proba_avg)
        }
    }

    # Save ensemble metrics
    pd.DataFrame(results).to_csv(os.path.join(out_dir, "ensemble_metrics.csv"))
    logging.info("Ensemble metrics saved at %s", os.path.join(out_dir, "ensemble_metrics.csv"))

    return results