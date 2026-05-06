import re
import nltk
from nltk.corpus import stopwords
import unidecode 


try:
    stopwords.words("french")
except LookupError:
    nltk.download("stopwords")

STOP_WORDS = set(stopwords.words("french"))
STOP_WORDS.remove("ne")
STOP_WORDS.remove("pas")

def normalize(text: str):
    """
    Clean and format text for NLP processing.
    """
    text = unidecode.unidecode(text)  # remove special characters
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # keep only letters
    text = text.lower()  # lowercase
    words = text.split()
    words = [w for w in words if w not in STOP_WORDS]  # remove stopwords
    text = " ".join(words)
    return text