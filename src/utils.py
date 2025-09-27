import os, random, logging, itertools
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

# ==============================
# Logging
# ==============================
def setup_logging(log_dir: str):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "run.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(log_path), logging.StreamHandler()]
    )
    logging.info("Logging initialized at %s", log_path)

# ==============================
# Reproducibility
# ==============================
def seed_everything(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)

# ==============================
# Directory Management
# ==============================
def ensure_dirs(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)

# ==============================
# Diversity Metric (Pairwise)
# ==============================
def compute_disagreement(model_preds: dict):
    """
    Compute pairwise disagreement between model predictions.
    model_preds: dict {model_name: predictions (0/1 array)}
    Returns: dict with disagreement scores (0 = identical, 1 = always disagree)
    """
    model_names = list(model_preds.keys())
    pairs = itertools.combinations(model_names, 2)
    results = {}
    for m1, m2 in pairs:
        p1, p2 = model_preds[m1], model_preds[m2]
        disagreement = np.mean(p1 != p2)
        results[f"{m1} vs {m2}"] = disagreement
    return results

# ==============================
# Ensemble Combination Metrics
# ==============================
def compute_ensemble_predictions(y_true, preds_list, rule="majority"):
    """
    Compute ensemble prediction using 1ooN, Majority, or NooN rules.
    """
    votes = np.sum(preds_list, axis=0)
    n = len(preds_list)

    if rule == "1ooN":  # at least one votes fraud
        y_pred = (votes >= 1).astype(int)
    elif rule == "NooN":  # all must agree
        y_pred = (votes == n).astype(int)
    else:  # Majority (default)
        y_pred = (votes >= (n/2)).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    sensitivity = tp / (tp + fn) if (tp+fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn+fp) > 0 else 0
    return sensitivity, specificity

def compute_ensemble_results(y_true, model_preds: dict):
    """
    Returns detailed results for each subset of models and rule (like Table VI/VII).
    """
    model_names = list(model_preds.keys())
    preds = [model_preds[m] for m in model_names]
    results = []

    for r in range(2, len(model_names)+1):
        for combo in itertools.combinations(range(len(model_names)), r):
            subset_names = tuple(model_names[i] for i in combo)
            subset_preds = [preds[i] for i in combo]
            for rule in ["1ooN", "Majority", "NooN"]:
                sens, spec = compute_ensemble_predictions(y_true, subset_preds, rule=rule)
                results.append({
                    "Models": subset_names,
                    "Rule": rule,
                    "Sensitivity": sens,
                    "Specificity": spec
                })

    return pd.DataFrame(results)

def compute_average_results(results_df):
    """
    Returns average Sens/Spec per N and rule (like Table VIII).
    """
    results_df["N"] = results_df["Models"].apply(len)
    avg = results_df.groupby(["N","Rule"])[["Sensitivity","Specificity"]].mean().reset_index()
    return avg