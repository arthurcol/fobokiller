import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
import tensorflow
import pickle
import os

path_sentences = os.path.join(os.path.dirname(__file__),'data/scrapping_cleaned_sentences.csv')
path_model = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model')
path_embed=os.path.join(os.path.dirname(os.path.dirname(__file__)),'embeddings.pkl')

sentences_df = pd.read_csv(path_sentences,index_col=0)
model = SentenceTransformer(path_model)

df_resto = sentences_df.groupby('alias').agg({ 'rate':'mean',
                                                'review':'nunique'
                                            })

def load_embedding():
    with open(path_embed, 'rb') as file:
        embedding = pickle.load(file)
    return embedding['embeddings']


def compute_sim_df(text, embedding, n_prox=None, min_review=0):
    input_encoded = model.encode(text)
    similarities = util.cos_sim(input_encoded, np.array(embedding))

    df_sim = sentences_df.assign(sim=similarities.T)

    if n_prox:
        df_filtered = df_sim.sort_values('sim', ascending=False)[:n_prox]
    else:
        df_filtered = df_sim.sort_values('sim', ascending=False)

    df_agg = df_filtered.groupby('alias').agg({
        'rate':'mean',
        'review':'nunique',
        'review_clean':lambda txt: ' // '.join(txt),
        #'review_clean':'first',
        'sim':'mean'
    })

    df_output = df_agg.merge(df_resto,
                             on='alias',
                             how='left',
                             suffixes=('_filtered', '_all')).reset_index()

    df_output['ratio'] = df_output['review_filtered'] / df_output['review_all']

    return df_output[df_output['review_all'] > min_review]


if __name__ == '__main__':
    load_embedding()
