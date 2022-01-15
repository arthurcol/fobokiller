import six

from google.cloud import bigquery

# Construct a BigQuery client object.
client = bigquery.Client()

PROJECT_ID = "wagon-bootcamp-328013"
table_id = "wagon-bootcamp-328013.trip.review"

job_config = bigquery.LoadJobConfig(schema=[
    bigquery.SchemaField("nom", "STRING"),
    bigquery.SchemaField("liens", "STRING"),
    bigquery.SchemaField("nb_avis", "STRING"),
    bigquery.SchemaField("type", "STRING"),
    bigquery.SchemaField("prix","STRING")
], )

# create a new datset
#client.create_dataset("trip")

# create a new table in that dataset ()
#client.create_table(f"{PROJECT_ID}.trip.review")
a = "1,2,3,4,5"
body = six.BytesIO(bytes(a))
client.load_table_from_file(body, table_id, job_config=job_config).result()
previous_rows = client.get_table(table_id).num_rows
assert previous_rows > 0

job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
)

uri = ""
load_job = client.load_table_from_uri(
    uri, table_id, job_config=job_config)  # Make an API request.

load_job.result()
