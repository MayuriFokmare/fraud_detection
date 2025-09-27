import os, argparse, logging
from src.utils import setup_logging, seed_everything, ensure_dirs
from src import preprocess as pp, features as fe
from src.train import split_data, build_models, save_model
from src.evaluate import evaluate_and_report
from src.ensemble import run_ensembles

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--fraud_type",
        required=True,
        choices=["fake_review", "payment", "chargeback", "merchant"],
        help="Fraud type to run experiment for"
    )
    ap.add_argument("--csv", required=True, help="Path to dataset CSV")
    ap.add_argument("--target", default="label", help="Target column name")
    return ap.parse_args()

def main():
    args = parse_args()

    # Setup experiment folders
    base_exp = os.path.join("experiments", args.fraud_type)
    models_dir = os.path.join(base_exp, "models")
    reports_dir = os.path.join(base_exp, "reports")
    ensembles_dir = os.path.join(base_exp, "ensembles")
    ensure_dirs(models_dir, reports_dir, ensembles_dir)

    setup_logging(reports_dir)
    seed_everything()

    # Load + clean dataset
    df = pp.load_csv(args.csv)
    df = pp.basic_clean(df)

    # Feature engineering
    df = fe.engineer(df)
    X, y = pp.split_features_target(df, args.target)

    # Preprocessor
    types = pp.detect_feature_types(X)
    preprocessor = pp.build_preprocessor(
        types["numeric"],
        types["categorical"],
        types["text"]
    )

    # Split data
    X_train, X_test, y_train, y_test = split_data(X, y)

    # Build and train models
    models = build_models(preprocessor)
    fitted = {}
    for name, pipe in models.items():
        pipe.fit(X_train, y_train)
        fitted[name] = pipe
        save_model(pipe, models_dir, name)

    # Evaluate
    evaluate_and_report(fitted, X_test, y_test, reports_dir)

    # Ensemble
    run_ensembles(fitted, X_test, y_test, ensembles_dir)

    logging.info("Finished experiment for %s", args.fraud_type)

if __name__ == "__main__":
    main()