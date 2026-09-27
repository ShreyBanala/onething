"""
OneThing - ML Model Training Pipeline
Trains two classifiers on Microsoft's MS-LaTTE dataset (10,101 tasks):
1. Location Classifier: Predicts location ('home', 'work'/campus, 'public')
2. Time-of-Day Classifier: Predicts time bucket ('morning', 'afternoon', 'evening', 'night')

Uses TF-IDF (word + character n-grams) + LogisticRegression with class_weight='balanced'
to handle class imbalance (e.g. overrepresented 'home' and 'evening').
Evaluates against a majority-class baseline and serializes models to models/.
"""

import os
import json
from collections import Counter
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

DATA_PATH = os.path.join("data", "MS-LaTTE.json")
MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

VALID_LOCATIONS = {"home", "work", "public"}
VALID_TIMES = {"morning", "afternoon", "evening", "night"}

SAMPLE_TASKS = [
    "study for psych quiz",
    "do laundry",
    "email professor",
    "grocery run",
    "call mom",
    "finish bio lab report",
    "meet group at campus library",
    "clean dorm room desk",
    "pick up prescription at pharmacy",
    "wind down and read before sleep"
]


def load_and_clean_data(data_path):
    """
    Loads MS-LaTTE.json and cleans votes:
    - Filters out votes where Known is 'no'
    - Splits comma-separated values
    - Strips weekday/weekend prefixes (wd-, we-) and ignores 'anytime'
    - Determines single consensus label per task via majority vote
    """
    print(f"📂 Loading dataset from {data_path}...")
    with open(data_path, "r", encoding="utf-8") as f:
        records = json.load(f)
    print(f"   Loaded {len(records):,} total tasks.")

    loc_texts, loc_labels = [], []
    time_texts, time_labels = [], []

    for item in records:
        title = item.get("TaskTitle", "").strip()
        if not title:
            continue

        # 1. Location Votes Processing
        loc_votes = []
        for v in item.get("LocJudgements", []):
            if v.get("Known", "").strip().lower() == "yes":
                for loc in v.get("Locations", "").split(","):
                    loc_clean = loc.strip().lower()
                    if loc_clean in VALID_LOCATIONS:
                        loc_votes.append(loc_clean)

        if loc_votes:
            # Majority vote consensus
            majority_loc = Counter(loc_votes).most_common(1)[0][0]
            loc_texts.append(title)
            loc_labels.append(majority_loc)

        # 2. Time-of-Day Votes Processing
        time_votes = []
        for v in item.get("TimeJudgements", []):
            if v.get("Known", "").strip().lower() == "yes":
                for t in v.get("Times", "").split(","):
                    t_clean = t.strip().lower()
                    # Strip wd- and we- prefixes
                    for prefix in ("wd-", "we-"):
                        if t_clean.startswith(prefix):
                            t_clean = t_clean[len(prefix):]
                    # Discard 'anytime', keep only 4 core buckets
                    if t_clean in VALID_TIMES:
                        time_votes.append(t_clean)

        if time_votes:
            # Majority vote consensus
            majority_time = Counter(time_votes).most_common(1)[0][0]
            time_texts.append(title)
            time_labels.append(majority_time)

    return (loc_texts, loc_labels), (time_texts, time_labels)


def build_pipeline():
    """
    Constructs a robust text classification pipeline combining:
    - Word-level TF-IDF (unigrams & bigrams)
    - Character-level TF-IDF (3-4 char n-grams inside word boundaries)
    - LogisticRegression with class_weight='balanced'
    """
    features = FeatureUnion([
        ("word_tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            sublinear_tf=True
        )),
        ("char_tfidf", TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 4),
            min_df=2,
            sublinear_tf=True
        ))
    ])

    classifier = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=42
    )

    return Pipeline([
        ("features", features),
        ("clf", classifier)
    ])


def train_and_evaluate(name, X, y, save_filename):
    """
    Trains model with 80/20 train/test split, evaluates against majority baseline,
    prints detailed classification reports, and saves pipeline to disk.
    """
    print(f"\n{'='*65}")
    print(f"🌿 TRAINING {name.upper()} CLASSIFIER")
    print(f"{'='*65}")
    print(f"Total samples: {len(X):,}")
    print("Class distribution:")
    counts = Counter(y)
    for label, count in counts.most_common():
        print(f"  - {label:<12}: {count:>5} ({count/len(y)*100:.1f}%)")

    # 80/20 train/test stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"\nTrain set: {len(X_train):,} samples | Test set: {len(X_test):,} samples")

    # Train our TF-IDF + LogisticRegression pipeline
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    model_acc = accuracy_score(y_test, y_pred)

    # Train majority-class baseline (always predicts most frequent training class)
    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(X_train, y_train)
    base_acc = baseline.score(X_test, y_test)
    most_common_class = baseline.predict(["dummy"])[0]

    # Display Metrics for Presentation & Judging
    print(f"\n📊 {name} Model Performance Results:")
    print(f"   ► Model Accuracy:           {model_acc*100:.2f}%")
    print(f"   ► Most-Common Baseline:     {base_acc*100:.2f}% (Always predicts '{most_common_class}')")
    diff = (model_acc - base_acc) * 100
    print(f"   ► Improvement over Guessing: {diff:+.2f} percentage points")

    print(f"\n📋 Detailed Classification Report for {name}:")
    print(classification_report(y_test, y_pred, digits=3))

    # Save trained model pipeline
    save_path = os.path.join(MODELS_DIR, save_filename)
    joblib.dump(pipeline, save_path)
    print(f"💾 Saved {name} model pipeline to {save_path}")

    return pipeline


def run_sanity_checks(loc_model, time_model, sample_tasks):
    """
    Runs both trained models on 10 realistic college student tasks,
    printing predictions and confidence scores in an ASCII table.
    """
    print(f"\n{'='*75}")
    print("🎓 SANITY CHECK: PREDICTIONS ON 10 SAMPLE COLLEGE TASKS")
    print(f"{'='*75}")

    header = f"{'Task Title':<34} | {'Location':<8} (Conf) | {'Time of Day':<10} (Conf)"
    print(header)
    print("-" * len(header))

    for task in sample_tasks:
        # Predict Location
        loc_pred = loc_model.predict([task])[0]
        loc_proba = np.max(loc_model.predict_proba([task])[0])

        # Predict Time
        time_pred = time_model.predict([task])[0]
        time_proba = np.max(time_model.predict_proba([task])[0])

        # Map 'work' to 'campus' for student context
        display_loc = "campus" if loc_pred == "work" else loc_pred

        print(
            f"{task:<34} | "
            f"{display_loc:<8} ({loc_proba:.0%}) | "
            f"{time_pred:<10} ({time_proba:.0%})"
        )
    print("-" * len(header))


def main():
    print("=" * 65)
    print("🌿 OneThing - Machine Learning Training Pipeline")
    print("=" * 65)

    # 1. Load and clean MS-LaTTE
    (loc_X, loc_y), (time_X, time_y) = load_and_clean_data(DATA_PATH)

    # 2. Train Location Classifier
    loc_model = train_and_evaluate(
        name="Location",
        X=loc_X,
        y=loc_y,
        save_filename="location_model.joblib"
    )

    # 3. Train Time-of-Day Classifier
    time_model = train_and_evaluate(
        name="Time-of-Day",
        X=time_X,
        y=time_y,
        save_filename="time_model.joblib"
    )

    # 4. Sanity check predictions
    run_sanity_checks(loc_model, time_model, SAMPLE_TASKS)

    print("\n✨ ML Training complete! Both models are ready in models/ for Step 4.")


if __name__ == "__main__":
    main()
