"""
train_model.py
---------------
Complete offline ML training pipeline for the Fake News Detection system.

Pipeline:
    Dataset -> Cleaning -> TF-IDF -> Train multiple models -> Evaluate ->
    Pick best model -> Save model + vectorizer with joblib

Run:
    python train_model.py
"""

import json
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, PassiveAggressiveClassifier
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                              precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

from utils.preprocess import clean_text

DATASET_DIR = "dataset"
MODEL_DIR = "saved_model"


def load_data():
    fake = pd.read_csv(f"{DATASET_DIR}/Fake.csv")
    real = pd.read_csv(f"{DATASET_DIR}/True.csv")

    fake["label"] = 1  # 1 = FAKE
    real["label"] = 0  # 0 = REAL

    df = pd.concat([fake, real], ignore_index=True)
    df["content"] = (df["title"].fillna("") + " " + df["text"].fillna(""))
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle
    return df[["content", "label"]]


def main():
    print("Step 1/6: Loading dataset...")
    df = load_data()
    print(f"  Loaded {len(df)} articles "
          f"({(df.label == 1).sum()} fake, {(df.label == 0).sum()} real)")

    print("Step 2/6: Cleaning text (lemmatization + stopword removal)...")
    df["clean"] = df["content"].apply(clean_text)

    print("Step 3/6: Splitting train/test (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        df["clean"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    print("Step 4/6: TF-IDF vectorization...")
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print("Step 5/6: Training & evaluating multiple models...")
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Passive Aggressive": PassiveAggressiveClassifier(max_iter=1000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
        "Naive Bayes": MultinomialNB(),
        "Linear SVM": LinearSVC(max_iter=2000),
    }

    results = {}
    best_name, best_model, best_f1 = None, None, -1

    for name, model in models.items():
        start = time.time()
        model.fit(X_train_vec, y_train)
        preds = model.predict(X_test_vec)
        elapsed = time.time() - start

        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds)
        rec = recall_score(y_test, preds)
        f1 = f1_score(y_test, preds)
        cm = confusion_matrix(y_test, preds).tolist()

        try:
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(X_test_vec)[:, 1]
            else:
                proba = model.decision_function(X_test_vec)
            auc = roc_auc_score(y_test, proba)
        except Exception:
            auc = None

        results[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4) if auc is not None else None,
            "confusion_matrix": cm,
            "train_time_sec": round(elapsed, 2),
        }

        print(f"  {name:22s} | Acc={acc:.4f} Prec={prec:.4f} Rec={rec:.4f} F1={f1:.4f}")

        if f1 > best_f1:
            best_f1, best_name, best_model = f1, name, model

    print(f"\nBest model: {best_name} (F1={best_f1:.4f})")

    print("Step 6/6: Saving model, vectorizer, and metadata...")
    joblib.dump(best_model, f"{MODEL_DIR}/model.pkl")
    joblib.dump(vectorizer, f"{MODEL_DIR}/vectorizer.pkl")

    metadata = {
        "best_model": best_name,
        "metrics": results,
        "feature_count": len(vectorizer.get_feature_names_out()),
        "train_size": len(X_train),
        "test_size": len(X_test),
    }
    with open(f"{MODEL_DIR}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved to {MODEL_DIR}/model.pkl, vectorizer.pkl, metadata.json")
    print("Training complete.")


if __name__ == "__main__":
    main()
