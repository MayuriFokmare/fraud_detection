import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import itertools
import numpy as np
from sklearn.metrics import confusion_matrix, roc_curve, auc, precision_recall_curve

# ==============================
# Confusion Matrix
# ==============================
def plot_confusion(y_true, y_pred, name, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(5,4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title(f"Confusion Matrix - {name}")
    path = os.path.join(out_dir, f"{name}_confusion.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path

# ==============================
# ROC Curve
# ==============================
def plot_roc(y_true, y_proba, name, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    roc_auc = auc(fpr, tpr)
    plt.figure(figsize=(5,4))
    plt.plot(fpr, tpr, color="blue", lw=2, label=f"AUC = {roc_auc:.3f}")
    plt.plot([0,1],[0,1], color="gray", linestyle="--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"ROC Curve - {name}")
    plt.legend(loc="lower right")
    path = os.path.join(out_dir, f"{name}_roc.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path

# ==============================
# Precision-Recall Curve
# ==============================
def plot_pr(y_true, y_proba, name, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    precision, recall, _ = precision_recall_curve(y_true, y_proba)
    plt.figure(figsize=(5,4))
    plt.plot(recall, precision, color="green", lw=2)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(f"Precision-Recall Curve - {name}")
    path = os.path.join(out_dir, f"{name}_pr.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path

# ==============================
# Diversity Heatmaps
# ==============================
def plot_diversity(y_true, model_preds: dict, out_dir: str, name: str):
    """
    y_true: array of true labels (0 = legit, 1 = fraud)
    model_preds: dict {model_name: predictions (0/1 array)}
    """
    os.makedirs(out_dir, exist_ok=True)

    df = pd.DataFrame(model_preds)
    df["true"] = y_true

    fraud = df[df["true"] == 1].drop(columns="true")
    plt.figure(figsize=(10,6))
    sns.heatmap(fraud.T, cmap=["white","green"], cbar=False)
    plt.title(f"{name} - Fraud cases detected")
    plt.ylabel("Models")
    plt.xlabel("Fraud samples")
    path_fraud = os.path.join(out_dir, f"{name}_fraud_diversity.png")
    plt.savefig(path_fraud, bbox_inches="tight")
    plt.close()

    legit = df[df["true"] == 0].drop(columns="true")
    plt.figure(figsize=(10,6))
    sns.heatmap(legit.T, cmap=["white","red"], cbar=False)
    plt.title(f"{name} - False alarms on legit cases")
    plt.ylabel("Models")
    plt.xlabel("Legit samples")
    path_legit = os.path.join(out_dir, f"{name}_falsealarm_diversity.png")
    plt.savefig(path_legit, bbox_inches="tight")
    plt.close()

    return path_fraud, path_legit

# ==============================
# Ensemble Combination ROC Scatter (Figure-5 style)
# ==============================
def evaluate_combination(y_true, preds_list):
    """Majority vote over given predictions list."""
    votes = np.sum(preds_list, axis=0)
    y_pred = (votes >= (len(preds_list)/2)).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    sensitivity = tp / (tp + fn) if (tp+fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn+fp) > 0 else 0
    return sensitivity, specificity

def plot_combination_roc(y_true, model_preds: dict, out_path: str):
    """
    Generate ROC-style scatter plots of Sensitivity vs Specificity
    for all model combinations (pairs, triplets, etc).
    model_preds: dict {model_name: predictions (0/1 array)}
    """
    model_names = list(model_preds.keys())
    preds = [model_preds[m] for m in model_names]

    plt.figure(figsize=(8,8))
    colors = {2:"red",3:"blue",4:"green",5:"orange"}

    # Plot individual models (black X)
    for name, p in model_preds.items():
        tn, fp, fn, tp = confusion_matrix(y_true, p).ravel()
        sens = tp/(tp+fn) if (tp+fn)>0 else 0
        spec = tn/(tn+fp) if (tn+fp)>0 else 0
        plt.scatter(spec, sens, marker="x", color="black", s=100, label=name)

    # Plot all combinations of models
    for r in range(2, len(model_names)+1):
        for combo in itertools.combinations(range(len(model_names)), r):
            subset_preds = [preds[i] for i in combo]
            sens, spec = evaluate_combination(y_true, subset_preds)
            plt.scatter(spec, sens, marker="o",
                        color=colors.get(r,"gray"), s=60,
                        label=f"{r}-model combo" if combo==(0,1) else "")

    plt.xlabel("Specificity")
    plt.ylabel("Sensitivity (Recall)")
    plt.title("ROC Points for Model Combinations")
    plt.legend()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
