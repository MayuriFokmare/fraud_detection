import pandas as pd
from sklearn.preprocessing import StandardScaler

def apply_strategy(fraud_type: str, X: pd.DataFrame) -> pd.DataFrame:
    """
    Apply preprocessing strategy depending on fraud type.
    This follows the Strategy Pattern: each fraud_type has its own data handling.
    """

    if fraud_type == "fake_review":
        # Example: lowercase text, strip whitespace
        if "review" in X.columns:
            X["review"] = X["review"].astype(str).str.lower().str.strip()

    elif fraud_type == "payment":
        # Example: scale numeric transaction amounts
        if "amount" in X.columns:
            scaler = StandardScaler()
            X["amount_scaled"] = scaler.fit_transform(X[["amount"]])

    elif fraud_type == "chargeback":
        # Example: create binary flag for suspicious merchants
        if "merchant" in X.columns:
            X["suspicious_merchant"] = X["merchant"].isin(
                ["fraud_store", "suspicious_shop"]
            ).astype(int)

    elif fraud_type == "merchant":
        # Example: clean up domain names
        if "domain" in X.columns:
            X["domain"] = X["domain"].astype(str).str.replace("www.", "", regex=False)

    # Return modified DataFrame
    return X