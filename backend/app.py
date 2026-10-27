import os
import pickle
import re
import string
import numpy as np
import pandas as pd
import tensorflow as tf
from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import sqlite3
from pathlib import Path
from datetime import datetime



# SQLite database location: same folder as app.py
DATABASE_PATH = Path(__file__).resolve().parent / "reviews.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS review_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review TEXT NOT NULL,
            ml_prediction TEXT,
            ml_confidence REAL,
            lstm_prediction TEXT,
            lstm_confidence REAL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Create the table if it doesn't already exist
init_db()



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load the trained machine-learning models
with open(os.path.join(BASE_DIR, "lr_model.pkl"), "rb") as f:
    lr_model = pickle.load(f)

with open(os.path.join(BASE_DIR, "nb_model.pkl"), "rb") as f:
    nb_model = pickle.load(f)

with open(os.path.join(BASE_DIR, "rf_model.pkl"), "rb") as f:
    rf_model = pickle.load(f)

with open(os.path.join(BASE_DIR, "vectorizer.pkl"), "rb") as f:
    vectorizer = pickle.load(f)


# CREATE FLASK SERVER
app = Flask(__name__)
CORS(app)


# TEXT CLEANING FUNCTION
# IMPORTANT: This should be the same cleaning used during model training.
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(
        str.maketrans('', '', string.punctuation)
    )
    return text




# LOAD TRAINED LSTM MODEL
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR, "lstm_model.keras"
)

TOKENIZER_PATH = os.path.join(
    BASE_DIR, "lstm_tokenizer.pkl"
)

lstm_model = tf.keras.models.load_model(MODEL_PATH)

with open(TOKENIZER_PATH, "rb") as f:
    lstm_tokenizer = pickle.load(f)

MAX_LENGTH = 150
#print("LSTM model loaded successfully!")

# GET BEST PREDICTION
def get_best_prediction(vec):
    # Logistic Regression
    lr_pred = lr_model.predict(vec)[0]
    lr_proba = max(
        lr_model.predict_proba(vec)[0]
    )

    # Naive Bayes
    nb_pred = nb_model.predict(vec)[0]
    nb_proba = max(
        nb_model.predict_proba(vec)[0]
    )

    # Random Forest
    rf_pred = rf_model.predict(vec)[0]
    rf_proba = max(
        rf_model.predict_proba(vec)[0]
    )

    # Choose model with highest confidence
    best_conf = max(
        lr_proba,
        nb_proba,
        rf_proba
    )

    if best_conf == lr_proba:
        final_pred = lr_pred
        
    elif best_conf == nb_proba:
        final_pred = nb_pred

    else:
        final_pred = rf_pred

    return {
        "prediction": (
            "Fake"
            if final_pred == 1
            else "Genuine"
        ),
        "confidence": round(
            float(best_conf),
            2
        )
    }


def get_lstm_prediction(review):
    cleaned_review = clean_text(review)

    sequence = lstm_tokenizer.texts_to_sequences(
        [cleaned_review]
    )

    padded = pad_sequences(
        sequence,
        maxlen=MAX_LENGTH,
        padding="post",
        truncating="post"
    )

    probability = float(
        np.asarray(
            lstm_model.predict(padded, verbose=0)
        ).reshape(-1)[0]
    )

    # Assumes label 1 = Fake and label 0 = Genuine
    prediction = 1 if probability >= 0.5 else 0

    confidence = (
        probability if prediction == 1
        else 1 - probability
    )

    return {
        "prediction": "Fake" if prediction == 1 else "Genuine",
        "confidence": round(confidence, 2)
    }



# SINGLE REVIEW
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    review = data.get("review")

    if not review or not str(review).strip():
        return jsonify({"error": "No review provided"}), 400

    # Clean the review
    cleaned_review = clean_text(review)

    # Convert cleaned text to TF-IDF numbers
    vec = vectorizer.transform([cleaned_review])

    # Get predictions from both models
    ml_result = get_best_prediction(vec)
    dl_result  = get_lstm_prediction(review)
 #lstm_result = get_lstm_prediction(review)

       # Extract ML prediction and confidence
    ml_label = (
        ml_result.get("prediction")
        if isinstance(ml_result, dict)
        else str(ml_result)
    )

    ml_confidence = (
        ml_result.get("confidence")
        if isinstance(ml_result, dict)
        else None
    )

    # Extract LSTM prediction and confidence
    lstm_label = (
        dl_result.get("prediction")
        if isinstance(dl_result, dict)
        else str(dl_result)
    )

    lstm_confidence = (
        dl_result.get("confidence")
        if isinstance(dl_result, dict)
        else None
    )

    # Save review and predictions in SQLite
    conn = get_db_connection()

    try:
        conn.execute(
            """
            INSERT INTO review_history (
                review,
                ml_prediction,
                ml_confidence,
                lstm_prediction,
                lstm_confidence,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(review),
                str(ml_label) if ml_label is not None else None,
                ml_confidence,
                str(lstm_label) if lstm_label is not None else None,
                lstm_confidence,
                datetime.now().astimezone().isoformat(
                    timespec="seconds"
                )
            )
        )
        conn.commit()
    finally:
        conn.close()

    # Return predictions to the React frontend
    return jsonify({
        "ml_prediction": ml_result,
        "lstm_prediction": dl_result
    })



@app.route("/history", methods=["GET"])
def get_review_history():
    conn = get_db_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                id,
                review,
                ml_prediction,
                ml_confidence,
                lstm_prediction,
                lstm_confidence,
                created_at
            FROM review_history
            ORDER BY id DESC
            """
        ).fetchall()

        history = [dict(row) for row in rows]

        return jsonify(history), 200

    except sqlite3.Error as error:
        return jsonify({
            "error": "Unable to retrieve review history",
            "details": str(error)
        }), 500

    finally:
        conn.close()


@app.route("/history/<int:review_id>", methods=["DELETE"])
def delete_review_history(review_id):
    conn = get_db_connection()

    try:
        cursor = conn.execute(
            "DELETE FROM review_history WHERE id = ?",
            (review_id,)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Review not found"}), 404

        return jsonify({"message": "Review deleted successfully"}), 200

    except sqlite3.Error as error:
        conn.rollback()
        return jsonify({
            "error": "Unable to delete review",
            "details": str(error)
        }), 500

    finally:
        conn.close()



# CSV + JSON FILE UPLOAD
@app.route("/upload", methods=["POST"])
def upload():
    # Get uploaded file
    file = request.files.get("file")
    if not file:
        return jsonify({
            "error": "No file uploaded"
        }), 400

    # Get file name
    filename = file.filename.lower()

    # Check file type
    if not filename.endswith((".csv", ".json")):
        return jsonify({
            "error": "Only CSV or JSON files are allowed"
        }), 400

    # Read CSV
    if filename.endswith(".csv"):
        try:
            df = pd.read_csv(file)
        except Exception as e:
            return jsonify({
                "error": f"Unable to read CSV file: {str(e)}"
            }), 400

    # Read JSON
    elif filename.endswith(".json"):
        try:
            df = pd.read_json(file)
        except Exception as e:
            return jsonify({
                "error": f"Unable to read JSON file: {str(e)}"
            }), 400

    # Check review column
    if "review" not in df.columns:
        return jsonify({
            "error": (
                "File must contain a 'review' column"
            )
        }), 400


    # Predict every review
    results = []
    for review in df["review"]:
        # Clean review
        cleaned_review = clean_text(review)
        
        # Convert to TF-IDF
        vec = vectorizer.transform(
            [cleaned_review]
        )

        # Predict
        result = get_best_prediction(vec)

        results.append({
            "review": review,
            "prediction": result["prediction"],
            "confidence": result["confidence"]
        })

    # Return results
    return jsonify(results)

# RUN SERVER
if __name__ == "__main__":
    app.run(debug=True)