import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

class TextFeatureExtractor:
    def __init__(self, max_features: int = 500):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            lowercase=True
        )

    def fit(self, df: pd.DataFrame) -> None:
        corpus = (df["description"].fillna("") + " " +
                  df["merchant"].fillna("") + " " +
                  df["mcc"].fillna("").astype(str))
        self.vectorizer.fit(corpus)

    def transform(self, df: pd.DataFrame):
        corpus = (df["description"].fillna("") + " " +
                  df["merchant"].fillna("") + " " +
                  df["mcc"].fillna("").astype(str))
        return self.vectorizer.transform(corpus)
