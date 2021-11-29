from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import List

resto_list = pd.read_csv("final_resto_list.csv",index_col=0)
print(resto_list.shape)

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
# details
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
