"""
utils/preprocess.py
--------------------
Shared text-preprocessing utilities used both at training time and at
prediction time, so that the exact same cleaning pipeline is applied
consistently (this is critical for ML correctness).

NOTE: This module is fully self-contained and works 100% OFFLINE.
It intentionally does NOT depend on nltk.corpus data (stopwords/wordnet),
because those corpora must be downloaded once via nltk.download() which
requires internet access and fails with a LookupError on a fresh machine
where that download was never run. Instead, a built-in stopword list and
a lightweight rule-based stemmer are used, so the app works immediately
after `pip install -r requirements.txt` with zero extra downloads.
"""

import re

# Built-in English stopword list (no external download required).
_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "could", "did", "do", "does",
    "doing", "down", "during", "each", "few", "for", "from", "further", "had",
    "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself",
    "just", "me", "might", "more", "most", "must", "my", "myself", "of", "off",
    "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over",
    "own", "same", "she", "should", "so", "some", "such", "than", "that", "the",
    "their", "theirs", "them", "themselves", "then", "there", "these", "they",
    "this", "those", "through", "to", "too", "under", "until", "up", "very",
    "was", "we", "were", "what", "when", "where", "which", "while", "who",
    "whom", "why", "will", "with", "would", "you", "your", "yours", "yourself",
    "yourselves", "also", "said",
}


def _simple_stem(word: str) -> str:
    """
    Lightweight suffix-stripping stemmer (no external corpus needed).
    Good enough for TF-IDF based classification while staying fully offline.
    """
    for suffix in ("ational", "ization", "fulness", "iveness", "ousness",
                   "ingly", "edly", "ising", "izing", "ation", "ements",
                   "ement", "ing", "ed", "ies", "es", "ly", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def clean_text(text: str) -> str:
    """
    Full cleaning pipeline:
    1. Lowercase
    2. Remove URLs, HTML tags, mentions, special chars
    3. Remove punctuation & digits
    4. Tokenize (simple whitespace split)
    5. Remove stopwords
    6. Lightweight stemming
    """
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", " ", text)
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = text.split()
    tokens = [t for t in tokens if t not in _STOPWORDS and len(t) > 2]
    tokens = [_simple_stem(t) for t in tokens]

    return " ".join(tokens)


def remove_punct(text: str) -> str:
    return text.translate(str.maketrans("", "", string.punctuation))
