import six
import datetime
from google.cloud import bigquery
import pandas as pd
# Construct a BigQuery client object.
client = bigquery.Client()

PROJECT_ID = "wagon-bootcamp-328013"
table_id = "wagon-bootcamp-328013.trip.listing5"
data = pd.read_csv("Paris1_TA.csv", header=None)

data[0] = [
    str(datetime.datetime.strptime(i, "%d/%m/%Y").strftime("%Y-%m-%d"))
    for i in data[0]
]
data[0]
data.rename(columns = { 0 : "date",
                       1 : "rating",
                       2 : "title",
                       3 : "review",
                       4 : "address",
                       5 : "name"}, inplace = True)
data = data.head()
job_config = bigquery.LoadJobConfig(schema=[
    bigquery.SchemaField("date", "DATE"),
    bigquery.SchemaField("rating", "FLOAT64"),
    bigquery.SchemaField("title", "STRING"),
    bigquery.SchemaField("review", "STRING"),
    bigquery.SchemaField("address", "STRING"),
    bigquery.SchemaField("name", "STRING")
], )

# create a new datset
#client.create_dataset("trip")

# create a new table in that dataset ()
client.create_table(f"{PROJECT_ID}.trip.listing5")


job = client.load_table_from_dataframe(data, table_id, )#job_config=job_config)
