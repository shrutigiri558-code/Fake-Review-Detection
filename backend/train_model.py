import pandas as pd
import re
import string
import pickle
import json

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# TEXT CLEANING FUNCTION
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

# csv - 
csv_data = pd.read_csv("fake_reviews.csv")
if "review" not in csv_data.columns or "label" not in csv_data.columns:
    raise ValueError(
        "CSV must contain 'review' and 'label' columns"
    )

# json - 
# json_data = pd.read_json("reviews.json")
with open("fake_reviews.json", "r", encoding="utf-8") as f:
    json_data = pd.DataFrame(json.load(f))

if "review" not in json_data.columns or "label" not in json_data.columns:
    raise ValueError(
        "JSON must contain 'review' and 'label' columns"
    )


data = pd.concat(
    [csv_data, json_data],
    ignore_index=True
)

data = data.dropna(subset=["review", "label"])

data = data.drop_duplicates(subset=["review", "label"])

print("CSV rows:", len(csv_data))
print("JSON rows:", len(json_data))
print("Combined rows:", len(data))

print("\nLabel distribution:")
print(data["label"].value_counts())
print("\nSample reviews for each label:")
print(data.groupby("label")["review"].first())


data["review"] = data["review"].apply(clean_text)
X = data["review"]
y = data["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=5000,
    ngram_range=(1, 2)
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

lr_model = LogisticRegression(max_iter=1000)
lr_model.fit(X_train_vec, y_train)

nb_model = MultinomialNB()
nb_model.fit(X_train_vec, y_train)

rf_model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

rf_model.fit(X_train_vec, y_train)


# EVALUATE ALL MODELS
lr_acc = accuracy_score(
    y_test,
    lr_model.predict(X_test_vec)
)

nb_acc = accuracy_score(
    y_test,
    nb_model.predict(X_test_vec)
)

rf_acc = accuracy_score(
    y_test,
    rf_model.predict(X_test_vec)
)


# DISPLAY ACCURACY
print("\nModel Accuracy:")

print(
    f"Logistic Regression Accuracy: "
    f"{lr_acc * 100:.2f}%"
)

print(
    f"Naive Bayes Accuracy: "
    f"{nb_acc * 100:.2f}%"
)

print(
    f"Random Forest Accuracy: "
    f"{rf_acc * 100:.2f}%"
)


# SAVE MODELS
pickle.dump(
    lr_model,
    open("lr_model.pkl", "wb")
)

pickle.dump(
    nb_model,
    open("nb_model.pkl", "wb")
)

pickle.dump(
    rf_model,
    open("rf_model.pkl", "wb")
)

pickle.dump(
    vectorizer,
    open("vectorizer.pkl", "wb")
)

print("\nAll models trained and saved successfully!")