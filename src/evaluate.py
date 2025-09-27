import os, logging
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report
)
from src.visualize import (
    plot_confusion, plot_roc, plot_pr,
    plot_diversity, plot_combination_roc
)
from src.utils import compute_ensemble_results, compute_average_results


def evaluate_and_report(models: dict, X_test, y_test, reports_dir: str):
    os.makedirs(reports_dir, exist_ok=True)
    results = {}
    model_preds = {}

    for name, model in models.items():
        # Predictions
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        model_preds[name] = y_pred  # store for diversity/ensemble analysis

        # Metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_proba)

        results[name] = {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "roc_auc": auc
        }

        # Save classification report
        with open(os.path.join(reports_dir, f"{name}_report.txt"), "w") as f:
            f.write(classification_report(y_test, y_pred))

        # Plots for each model
        plot_confusion(y_test, y_pred, name, reports_dir)
        plot_roc(y_test, y_proba, name, reports_dir)
        plot_pr(y_test, y_proba, name, reports_dir)

        logging.info(
            "%s | Acc=%.3f Prec=%.3f Rec=%.3f F1=%.3f AUC=%.3f",
            name, acc, prec, rec, f1, auc
        )

    # Save overall summary
    pd.DataFrame(results).T.to_csv(os.path.join(reports_dir, "metrics_summary.csv"))

    # 🔹 Additional ensemble/diversity analysis
    if len(model_preds) > 1:
        # Diversity heatmaps (green/red)
        plot_diversity(y_test.values, model_preds, reports_dir, "diversity")

        # ROC scatter for combinations (Figure-5 style)
        plot_combination_roc(
            y_test.values,
            model_preds,
            os.path.join(reports_dir, "combination_roc.png")
        )

        # Ensemble tables (Table VI–VIII style)
        df_results = compute_ensemble_results(y_test.values, model_preds)
        df_results.to_csv(os.path.join(reports_dir, "ensemble_detailed.csv"), index=False)

        df_avg = compute_average_results(df_results)
        df_avg.to_csv(os.path.join(reports_dir, "ensemble_avg.csv"), index=False)

        logging.info("Saved ensemble results: detailed and averaged.")

    return results