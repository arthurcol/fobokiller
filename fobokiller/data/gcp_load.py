import six

from google.cloud import bigquery
import pandas as pd
import pandas_gbq
# Construct a BigQuery client object.
#client = bigquery.Client()

projet_id = "wagon-bootcamp-328013"
table_id = "wagon-bootcamp-328013.trip.comment"

#
data = pd.read_csv("data/Paris1b_TA.csv", header = None)

#
data[0] = [i.replace("/", "-") for i in data[0]]

#

data.rename(columns={
    0: "date",
    1: "note",
    2: "titre",
    3: "commentaire",
    4: "adresse",
    5: "nom"
}, inplace = True)


data["date"] = pd.to_datetime(data["date"])

pandas_gbq.to_gbq(data,table_id, projet_id, if_exists="append")
