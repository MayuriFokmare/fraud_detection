import pandas as pd
from .model_loader import load_model
from . import report_generator as rg


class FraudService:
    def __init__(self, fraud_type: str, model_name: str = "random_forest"):
        """
        Service class to handle fraud prediction and reporting.
        """
        self.fraud_type = fraud_type
        self.model_name = model_name
        self.model = load_model(fraud_type, model_name)

    def predict(self, df: pd.DataFrame):
        """
        Apply preprocessing and run model predictions.
        Returns:
            tuple -> (summary_dict, dataframe_with_predictions)
        """
        # Drop label if present
        X = df.drop(columns=["label"], errors="ignore")

        # Run predictions
        df["fraud_prediction"] = self.model.predict(X)
        df["fraud_probability"] = self.model.predict_proba(X)[:, 1]

        # Build summary
        summary = {
            "fraud_type": self.fraud_type,
            "model_used": self.model_name,
            "total_records": len(df),
            "fraudulent_cases": int(df["fraud_prediction"].sum()),
            "fraud_rate": round(float(df["fraud_prediction"].mean()), 3),
        }

        return summary, df

    def generate_report(self, df: pd.DataFrame, view_type: str):
        """
        Generate reports based on requested view_type.
        """
        if view_type == "summary":
            return rg.generate_summary(self.fraud_type, self.model_name, df)
        elif view_type == "breakdown":
            return rg.generate_breakdown(self.fraud_type, df)
        elif view_type == "probabilities":
            return rg.generate_probabilities(df)
        else:
            raise ValueError(f"Unsupported view_type: {view_type}")