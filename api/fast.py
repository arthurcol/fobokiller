from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import List
from fobokiller.cosim import compute_sim_df, load_embedding,summary_reviews

resto_list = pd.read_csv("final_resto_list.csv",index_col=0)
print(resto_list.shape)
embedding = load_embedding()
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
    return pd_liste.to_dict(
    )

@app.get("/summary_reviews")
def sr(text,n_best=10, n_prox=3000, min_review =0):
    min_review =int(min_review)
    print(type(n_prox))
    if  pd.isna(n_prox) :
        pass
    else :
        n_prox = int(n_prox)
    temp = compute_sim_df(text, embedding, n_prox, min_review)
    print("temp OK ")
    n_best = int(n_best)
    result = summary_reviews(temp, n_best)
    print("summary_reviews OK ")
    return result.to_dict()
