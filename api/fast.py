from fobokiller.heatmap import load_reviews_dataset, heatmap_sentences, \
load_model,apply_heatmap_html,apply_heatmap_polarity

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import List

from fobokiller.cosim import compute_sim_df, load_embedding, summary_reviews
#words/sentences  preprocessing
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras import backend as K
#modeling
from tensorflow import GradientTape
import tensorflow as tf#modeling
from tensorflow.keras import models, layers

resto_list = pd.read_csv("api/final_resto_list.csv", index_col=0)

embedding = load_embedding()

reviews_dataset = load_reviews_dataset()

model_heatmap = load_model()


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
def index():
    return {"greeting": "Hello world"}


#Input list of restaurant (alias)
# detail
@app.get("/detail")
def get_details(alias):

    alias = [alias]
    pd_liste = resto_list.loc[resto_list['alias'].isin(alias), :]
    return pd_liste.to_dict()



@app.get("/details/")
def read_items(alias: List[str] = Query(None)):
    print(alias)
    pd_liste = resto_list.loc[resto_list['alias'].isin(alias), :]
    print(pd_liste)

    return pd_liste.to_dict()


@app.get("/summary_reviews")
def sr(text, n_best=10, n_prox=3000, min_review=0):
    min_review = int(min_review)
    print(type(n_prox))
    if pd.isna(n_prox):
        pass
    else:

        n_prox = int(n_prox)
    temp = compute_sim_df(text, embedding, n_prox, min_review)
    n_best = int(n_best)
    result = summary_reviews(temp, n_best)
    return result.to_dict()



@app.get("/summary_reviews2")
def sr2(text, n_best=1, n_prox=3000, min_review=10):

    #setting types
    min_review = int(min_review)
    if pd.isna(n_prox):
        pass
    else:
        n_prox = int(n_prox)
    n_best = int(n_best)

    #loading datasets
    results = compute_sim_df(text, embedding, n_prox, min_review)
    summary = summary_reviews(results, n_best)
    results['is_sim'] = 1
    summary['is_in_summary'] = 1
    results_trimed = results.drop(
        columns=['alias', 'rate', 'review_sentences'])

    #merging datasets and house cleaning

    tmp_df = reviews_dataset.merge(results_trimed,
                                   on='review_clean',
                                   how='left')
    tmp_df['is_sim'].fillna(0, inplace=True)
    all_df = tmp_df.merge(summary, on='alias', how='left')
    all_df.fillna(0, inplace=True)
    all_df = all_df[all_df["is_in_summary"]==1]

    #apply heatmap for html and polarity score
    all_df['reviews_heatmaps_html'] = all_df.apply(apply_heatmap_html,axis=1)
    all_df['reviews_heatmaps_polarity'] = all_df.apply(apply_heatmap_polarity, axis=1)
    ####  metrics for the val of the request
    all_df['request_metric'] = all_df[(all_df['is_in_summary'] == 1) & (
        all_df['is_sim'] == 1)]['nb_sentences'].sum() *100 /3000
    summary_reconstructed = all_df.groupby('alias').agg({
        'review_clean':
        list,
        'nb_sentences':
        'mean',
        'nb_review':
        'mean',
        'metric sim_ratio':
        'mean',
        'rate_filtered':'mean',
        'reviews_heatmaps_html':
        list,
        'reviews_heatmaps_polarity':
        list
    })

    #print("check")
    #print(type(summary_reconstructed))
    #print(summary_reconstructed.columns)
    #print(summary_reconstructed.shape)
    output_json = summary_reconstructed.to_dict()
    return output_json
