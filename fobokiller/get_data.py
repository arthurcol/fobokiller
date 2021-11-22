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
from dotenv import load_dotenv, dotenv_values
from fobokiller.utils import subzones_paris
from os.path import join,dirname

env_path = join(dirname(dirname(__file__)), '.env')

api_key = dotenv_values()["KEY1"]



def get_restaurants(centers, radius, api_key):
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


centers, radius = subzones_paris(4)



if __name__ == '__main__':
    centers, radius = subzones_paris(4)
    df = get_restaurants(centers, radius, api_key)
