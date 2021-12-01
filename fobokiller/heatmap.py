### IMPORTS ###

#canonical
from sys import path
from h5py._hl import dataset
import pandas as pd
import numpy as np
import os
import pickle

#words/sentences  preprocessing
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras import backend as K

from tensorflow import GradientTape
import tensorflow as tf

from IPython.display import HTML, display

#modeling
from tensorflow.keras import models, layers

#cosim

from fobokiller.cosim import load_embedding,compute_sim_df,summary_reviews

def load_model():
    path_model = os.path.join(os.path.dirname(os.path.dirname(__file__)),'model_heatmap')
    model = models.load_model(path_model)
    return model

def load_reviews_dataset():
    path_reviews_all = os.path.join(os.path.dirname(__file__),
                                    'data/scrapping_cleaned_sentences.csv')
    dataset = pd.read_csv(path_reviews_all,index_col=0)
    embedding=load_embedding()
    dataset = dataset.assign(embedding=[*np.array(embedding)])
    dataset = dataset.groupby('review_clean').agg({
                                                'alias': 'first',
                                                'rate': 'mean',
                                                'review_sentences': list,
                                                'embedding': list,
                                            }).reset_index()
    dataset['review_sentences_trimed'] = dataset['review_sentences'].apply(
        lambda list_: list_[:30])

    return dataset


def creating_query_dataset(embedding,reviews_dataset,query, n_prox, min_review,n_best):
    #loading data
    results = compute_sim_df(query,embedding,n_prox=n_prox,min_review=min_review)
    summary = summary_reviews(results,n_best=n_best)

    #creating is_sim & is_in_summary columns
    results['is_sim'] = 1
    summary['is_in_summary'] = 1

    #merging datasets
    results_trimed = results.drop(columns=['alias', 'rate', 'review_sentences'])
    tmp_df = reviews_dataset.merge(results_trimed, on='review_clean', how='left')
    tmp_df['is_sim'].fillna(0, inplace=True)
    all_df = tmp_df.merge(summary, on='alias', how='left')
    all_df.fillna(0, inplace=True)

    return all_df



def heatmap_sentences(review_sentences, review_embedded, model):
    #padding
    review_embedded = pad_sequences([review_embedded],
                                    dtype='float32',
                                    padding='post',
                                    maxlen=30)
    # predict
    preds = model.predict(review_embedded)
    #gradient tape
    with tf.GradientTape() as tape:
        class_idx = np.argmax(preds[0]) #a priori useless always return 0
        last_conv_layer = model.get_layer('conv1d')
        iterate = tf.keras.models.Model([model.inputs],
                                        [model.output, last_conv_layer.output])
        model_out, last_conv_layer = iterate(review_embedded)
        class_out = model_out[:, class_idx]
        grads = tape.gradient(class_out, last_conv_layer)
        pooled_grads = tf.reduce_mean(grads)

    heatmap = tf.reduce_mean(tf.multiply(pooled_grads, last_conv_layer),
                             axis=-1)
    heatmap = np.maximum(heatmap, 0)
    heatmap /= np.max(heatmap)

    html = ""
    for i, j in enumerate(review_sentences):
        html += f"<span style='background-color:rgba(0,{heatmap[0][i]*255},0,0.6)'>{j} </span>"

    return html
