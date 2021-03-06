FROM python:3.8.12-buster

COPY requirements_test.txt /requirements_test.txt

RUN pip install joblib

RUN pip install --upgrade pip

RUN pip install -r requirements_test.txt

COPY embeddings.pkl /embeddings.pkl

COPY api /api

COPY model /model

COPY model_heatmap /model_heatmap

COPY fobokiller /fobokiller

COPY  fobokiller/data/scrapping_cleaned_sentences.csv /fobokiller/data/scrapping_cleaned_sentences.csv

COPY final_resto_list.csv/ final_resto_list.csv

CMD uvicorn api.fast:app --host 0.0.0.0 --port $PORT
