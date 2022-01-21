import six

from google.cloud import bigquery
import pandas as pd
# Construct a BigQuery client object.
client = bigquery.Client()

PROJECT_ID = "wagon-bootcamp-328013"
table_id = "wagon-bootcamp-328013.trip.listing"
data = pd.read_csv("Paris1_TA.csv", header=None)

data[0] = [i.replace("/", "-") for i in data[0]]


job_config = bigquery.LoadJobConfig(schema=[
    bigquery.SchemaField("date", "DATE"),
    bigquery.SchemaField("rating", "FLOAT"),
    bigquery.SchemaField("title", "STRING"),
    bigquery.SchemaField("review", "STRING"),
    bigquery.SchemaField("address", "STRING"),
    bigquery.SchemaField("name", "STRING")
], )

# create a new datset
#client.create_dataset("trip")

# create a new table in that dataset ()
client.create_table(f"{PROJECT_ID}.trip.listing")

client = bigquery.Client()
job = client.load_table_from_dataframe(data, table_id, job_config=job_config)
