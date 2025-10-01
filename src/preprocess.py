import logging
import pandas as pd
from typing import Tuple, List, Dict
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

# ==============================
# Generic utilities
# ==============================
def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    logging.info("Loaded %s with %d rows, %d columns", path, df.shape[0], df.shape[1])
    return df

def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    before = df.shape[0]
    df = df.drop_duplicates()
    logging.info("Dropped %d duplicate rows", before - df.shape[0])
    return df

def split_features_target(df: pd.DataFrame, target_col: str) -> Tuple[pd.DataFrame, pd.Series]:
    y = df[target_col]
    if y.dtype == "object":  
        y = y.astype(str).str.strip().str.lower().map(
            lambda v: 1 if v in {"1", "true", "yes", "cg", "fraud", "fraudulent"} else 0
        )
    X = df.drop(columns=[target_col])
    return X, y

def detect_feature_types(X: pd.DataFrame) -> Dict[str, List[str]]:
    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = X.select_dtypes(exclude=["number"]).columns.tolist()
    text_cols = [c for c in categorical_cols if c.lower() in {"text","text_","review","comment","description"}]
    categorical_cols = [c for c in categorical_cols if c not in text_cols]
    return {"numeric": numeric_cols, "categorical": categorical_cols, "text": text_cols}

def build_preprocessor(numeric_cols: List[str], categorical_cols: List[str], text_cols: List[str]) -> ColumnTransformer:
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])
    text_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=2000, ngram_range=(1,2)))
    ])

    transformers = []
    if numeric_cols:
        transformers.append(("num", numeric_pipeline, numeric_cols))
    if categorical_cols:
        transformers.append(("cat", categorical_pipeline, categorical_cols))
    if text_cols:
        transformers.append(("text", text_pipeline, text_cols[0]))  

    preprocessor = ColumnTransformer(transformers)
    return preprocessor

# ==============================
# Dataset specific loaders
# ==============================
def load_fake_review(path="data/fake_review/processed/fake_reviews.csv"):
    df = basic_clean(load_csv(path))
    X, y = split_features_target(df, "label")
    return X, y

def load_payment(path="data/payment/processed/payment.csv"):
    df = basic_clean(load_csv(path))
    X, y = split_features_target(df, "label")
    return X, y

def load_chargeback(path="data/chargeback/processed/df.csv"):
    df = basic_clean(load_csv(path))
    target_col = "label" if "label" in df.columns else df.columns[-1]
    X, y = split_features_target(df, target_col)
    return X, y

def load_merchant(path="data/merchant/processed/Fraudulent_online_shops_dataset.csv"):
    df = basic_clean(load_csv(path))
    target_col = "label" if "label" in df.columns else "fraudulent"
    X, y = split_features_target(df, target_col)
    return X, y
