import pandas as pd
import os
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime


def clear_data_text(text, language='english'):
    """
    Returns a clean text as a string. Default language = english.
    Cleaning includes : removing punct, digit and \\n, stopwords, informations
    related to author review, and lowercase.
    """
    #remove before the begin of the comment
    for i in range(5):
        pos = 0
        pos = text.find('\n')
        text = text[pos + 1:]

    #remove punctuation
    for punctuation in string.punctuation:
        text = text.replace(punctuation, '')

    # remove number
    text = ''.join(word for word in text if not word.isdigit())

    #pass in lowercase
    text = text.lower()

    #remove stop words
    stop_words = set(stopwords.words(language))

    #text to list of word
    word_tokens = word_tokenize(text)

    #list to string
    text = " ".join([w for w in word_tokens if not w in stop_words])

    #remove after the end of the comment
    if text.endswith('useful funny cool'):
        text = text[:-len('useful funny cool')]
        text = text.strip()
    if text.startswith('updated review'):
        text = text.split('useful funny cool', 1)[0]
        text = text[len('updated review'):]
        text = text.strip()
    if text.startswith('photos'):
        text = text[len('photos'):]
        text = text.strip()
    if text.startswith('photo'):
        text = text[len('photo'):]
        text = text.strip()
    text = text.strip()
    return text


def change_date(date, format_='%m/%d/%Y'):
    """
    Convert date into a datetime object with format used on yelp
    """
    date_tmp = datetime.strptime(date, format_)
    return date_tmp


def keep_digit(rate):
    """
    Returns only the first digit of a string
    """
    for char in rate.split():
        if char.isdigit():
            return int(char)
    pass

def cleaner(data):
    data['review_clean'] = data['review'].apply(clear_data_text)
    data['date'] = data['date'].apply(change_date)
    data['rate'] = data['rate'].apply(keep_digit)
    return data

if __name__ == '__main__':
    #load data
    path_data = os.path.join(os.path.dirname(__file__), 'data/scrapping.csv')
    data = pd.read_csv(path_data,index_col=0)
    #call cleaner function
    data_clean = cleaner(data)
    path_storage = os.path.join(os.path.dirname(__file__),
                                'data/scrapping_cleaned.csv')
    data_clean.to_csv(path_storage)
