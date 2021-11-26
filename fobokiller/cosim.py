import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
import tensorflow
import pickle
import os

path_full_dataset = os.path.join(os.path.dirname(__file__),'data/scrapping_cleaned_sentences.csv')
path_model = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model')
path_embed=os.path.join(os.path.dirname(os.path.dirname(__file__)),'embeddings.pkl')

df_full = pd.read_csv(path_full_dataset,index_col=0)
model = SentenceTransformer(path_model)

df_all_resto = df_full.groupby('alias').agg({ 'rate':'mean',
                                                'review':'nunique'
                                            })

def load_embedding():
    with open(path_embed, 'rb') as file:
        embedding = pickle.load(file)
    return embedding['embeddings']


def compute_sim_df(text, embedding, n_prox=None, min_review=0):
    input_encoded = model.encode(text)
    similarities = util.cos_sim(input_encoded, np.array(embedding))

    df_sim = df_full.assign(sim=similarities.T)

    if n_prox:
        df_sentences = df_sim.sort_values('sim', ascending=False)[:n_prox]
    else:
        df_sentences = df_sim.sort_values('sim', ascending=False)

    df_agg = df_sentences.groupby('alias').agg({
        'rate': 'mean',
        'review': 'nunique',
        #'review_sentences':'first',
        #'review_clean':lambda txt: ' // '.join(txt),
        'sim':'mean'
    })

    df_resto = df_agg.merge(df_all_resto,
                             on='alias',
                             how='left',
                             suffixes=('_filtered', '_all')).reset_index()

    df_resto['ratio'] = df_resto['review_filtered'] / df_resto['review_all']

    df_resto = df_resto.sort_values('ratio')
    df_resto = df_resto[df_resto['review_all'] > min_review]

    df_final = df_sentences.merge(df_resto,
                                 on='alias',
                                 how='left',
                                 suffixes=('_s', '_r'))

    df_final.drop(columns=['review'],inplace=True)

    return df_final


if __name__ == '__main__':
    load_embedding()
