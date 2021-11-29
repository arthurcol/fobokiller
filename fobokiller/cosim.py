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

    df_final['metric']=df_final['ratio']*df_final['sim_r']

    df_final.drop(columns=['review'],inplace=True)

    return df_final

def summary_reviews(result,n_best):
    result.fillna(0,inplace=True)

    # select n_best first restaurants with higher sim_r
    higher_sim_r = sorted(result['metric'].unique())[-n_best - 1:]
    best_sim_r = result[result['metric'] > higher_sim_r[0]]

    reviews = best_sim_r.groupby('alias').agg({
        'review_clean': [set,'count'],
        'review_filtered':'first',
        'metric':'mean'
    })

    reviews.rename(columns={'set':'reviews',
                            'count':'nb_sentences',
                            'first':'nb_review',
                            'mean':'metric sim_ratio'},inplace=True)

    reviews = reviews.droplevel(level=0, axis=1)

    reviews['sentences_pond'] = reviews['nb_sentences']/reviews['nb_sentences'].sum()
    reviews['metric_pond'] = reviews['sentences_pond'] * reviews[
        'metric sim_ratio']

    return reviews.sort_values('metric sim_ratio')


if __name__ == '__main__':
    load_embedding()
