import pandas as pd
import requests
from selenium import webdriver
import matplotlib.pyplot as plt
import folium
import time
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from dotenv import load_dotenv, dotenv_values, find_dotenv
from fobokiller.utils import subzones_paris
from os.path import join,dirname
import os

env_path = find_dotenv()
#env_path = join(dirname(dirname(__file__)), '.env')
load_dotenv(env_path)

#api_key = dotenv_values()["YELP_KEY"]

api_key = os.getenv('YELP_KEY')


def get_restaurants(centers, radius):
    """
    Returns DataFrame of restaurants in Paris
    """
    headers = {'Authorization': f'Bearer {api_key}'}
    url = 'https://api.yelp.com/v3/businesses/search'

    data = []

    for i, c in enumerate(centers):
        print(f'---------- Requesting API for subzone #{i+1} ----------')
        for offset in range(0, 200, 50):
            print(
                f'   ------- Requesting API with offset = {offset} -------   ')
            params = {
                'limit': 50,
                'categories': ['restaurants'],
                'sort_by': 'review_count',
                'offset': offset,
                'latitude': c[0],
                'longitude': c[1],
                'radius': int(radius)
            }

            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data += response.json()['businesses']
            elif response.status_code == 400:
                print('400 Bad Request')
                break

    print(f'#####   Request completed, {len(data)} businesses fetched   ###')
    return data


### Create DF for Yelp data


def create_df_yelp(data):

    df = pd.DataFrame(columns=[
        'alias', 'name', 'url', 'categories', 'latitude', 'longitude',
        'address', 'zip_code', 'price', 'rating', 'review_count'
    ])

    features_to_loop = [
        'alias', 'name', 'url', 'categories', 'price', 'rating', 'review_count'
    ]

    #populate DF
    #if condition to avoid raising errors in case restaurant doesn't have all informations

    for i, d in enumerate(data):

        for f in features_to_loop:
            if f in d:
                df.loc[i, f] = d[f]
            else:
                df.loc[i, f] = ''

        if 'location' in d:
            if 'latitude' in d['coordinates']:
                df.loc[i, 'latitude'] = d['coordinates']['latitude']
            else:
                df.loc[i, 'latitude'] = ''

            if 'longitude' in d['coordinates']:
                df.loc[i, 'longitude'] = d['coordinates']['longitude']
            else:
                df.loc[i, 'longitude'] = ''

            if 'address1' in d['location']:
                df.loc[i, 'address'] = d['location']['address1']
            else:
                df.loc[i, 'address'] = ''

            if 'zip_code' in d['location']:
                df.loc[i, 'zip_code'] = d['location']['zip_code']
            else:
                df.loc[i, 'zip_code'] = 0

    #clean DF
    #dtypes
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)
    df['zip_code'] = df['zip_code'].replace('', 0).astype(int)
    df['rating'] = df['rating'].astype(float)
    df['review_count'] = df['review_count'].astype(float)

    #url
    df['url'] = df['url'].apply(lambda txt: txt.split('?', 1)[0])

    #price
    prices = {'€': '1', '€€': '2', '€€€': '3', '€€€€': '4'}

    for euro, num in prices.items():
        df['price'] = df['price'].replace(euro, num)

    df['price'] = df['price'].replace('', 0).astype(int)

    #categories
    df['categories'] = df['categories'].apply(
        lambda dicts: ', '.join([d['alias'] for d in dicts]))

    return df.drop_duplicates()



def get_place_google_id(name,latitude,longitude):

    url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
    params={
        'key' : "AIzaSyDATqRkvgk2P1bbIu6itIq2jAuiaPxnhfc",
        'input' : name,
        'inputtype' : 'textquery',
        'locationbias' : f'point:{latitude},{longitude}'
    }

    response = requests.get(url,params=params)

    #if conditions to avoid raising errors
    if response.status_code != 200:
        return ''

    if 'candidates' in response.json():
        response = response.json()['candidates']
        if len(response)==0:
            return ''
        if 'place_id' in response[0]:
            return response[0]['place_id']

    return ''



## Get place url


def get_place_google_url(place_id):
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = {
        'key': 'AIzaSyDATqRkvgk2P1bbIu6itIq2jAuiaPxnhfc',
        'place_id': place_id,
        'fields': 'url'
    }

    response = requests.get(url, params=params)

    #if conditions to avoid raising errors
    if response.status_code != 200:
        return ''

    if 'result' in response.json():
        response = response.json()['result']
        if 'url' in response:
            return response['url']

    return ''



if __name__ == '__main__':
    centers, radius = subzones_paris(1)
    df = get_restaurants(centers, radius)
    df = create_df_yelp(df)
    id_ = get_place_google_id(df.loc[0, 'name'], df.loc[0, 'latitude'],
                              df.loc[0, 'longitude'])
    lien = get_place_google_url(id_)
    print(lien)
