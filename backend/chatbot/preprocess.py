import nltk
import string
import re

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()


def preprocess_text(text):

    # convert to lowercase
    text = text.lower()

    # remove numbers
    text = re.sub(r'\d+', '', text)

    # tokenize sentence
    tokens = word_tokenize(text)

    processed_tokens = []

    for word in tokens:

        # remove punctuation and stopwords
        if word not in stop_words and word not in string.punctuation:

            # apply stemming
            stemmed = stemmer.stem(word)

            processed_tokens.append(stemmed)

    return " ".join(processed_tokens)