import nltk
import numpy as np
from nltk.stem.porter import PorterStemmer

stemmer = PorterStemmer()


def tokenize(sentence: str) -> list[str]:
    return nltk.word_tokenize(sentence)


def stem(word: str) -> str:
    return stemmer.stem(word.lower())


def bag_of_words(tokenized_sentence: list[str], words: list[str]) -> list[int]:
    tokenized_sentence = [stem(word) for word in tokenized_sentence]

    bag = np.zeros(len(words), dtype=np.float32)

    for index, word in enumerate(words):
        if word in tokenized_sentence:
            bag[index] = 1.0

    return bag
