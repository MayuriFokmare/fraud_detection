import os, logging, joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from src.preprocess import (
    detect_feature_types, build_preprocessor,
    load_fake_review, load_payment, load_chargeback, load_merchant
)
from src.evaluate import evaluate_and_report
from src.utils import ensure_dirs

# ==============================
# Split helper
# ==============================
def split_data(X, y, test_size=0.3, seed=42):
    return train_test_split(X, y, test_size=test_size, stratify=y, random_state=seed)

# ==============================
# Build pipelines
# ==============================
def build_models(preprocessor):
    models = {
        "log_reg": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "random_forest": RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42),
        "xgboost": XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=42)
    }
    pipelines = {name: Pipeline([("preprocessor", preprocessor), ("model", model)])
                 for name, model in models.items()}
    return pipelines

# ==============================
# Save trained model
# ==============================
def save_model(pipe, model_dir: str, name: str):
    os.makedirs(model_dir, exist_ok=True)
    path = os.path.join(model_dir, f"{name}.joblib")
    joblib.dump(pipe, path)
    logging.info("Saved model: %s", path)
    return path

# ==============================
# Training entry point
# ==============================
def train_all(base_exp_dir="experiments"):
    datasets = {
        "fake_review": load_fake_review,
        "payment": load_payment,
        "chargeback": load_chargeback,
        "merchant": load_merchant
    }

    for fraud_type, loader in datasets.items():
        logging.info("=== Training for %s fraud ===", fraud_type)

        # Load  split
        X, y = loader()
        X_train, X_test, y_train, y_test = split_data(X, y)

        # Preprocessor
        feat_types = detect_feature_types(X_train)
        preprocessor = build_preprocessor(
            feat_types["numeric"], feat_types["categorical"], feat_types["text"]
        )

        # Models
        pipelines = build_models(preprocessor)

        # Train and save
        model_dir = os.path.join(base_exp_dir, fraud_type, "models")
        reports_dir = os.path.join(base_exp_dir, fraud_type, "reports")
        ensure_dirs(model_dir, reports_dir)

        for name, pipe in pipelines.items():
            pipe.fit(X_train, y_train)
            save_model(pipe, model_dir, name)

        # Evaluation
        evaluate_and_report(pipelines, X_test, y_test, reports_dir)

        logging.info("Finished training for %s fraud", fraud_type)
