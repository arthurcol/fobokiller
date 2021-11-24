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
import csv

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
        'key' :  os.getenv('GOOGLE_PLACE_KEY'),
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
        'key': os.getenv('GOOGLE_PLACE_KEY'),
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




### Get all reviews from a Google page


def get_reviews_google(url,
                       scroll_limit=None,
                       quiet_mode=True,
                       return_count=False):

    # Import the webdriver
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs',
                                    {'intl.accept_languages': 'en,en_US'})
    if quiet_mode:
        options.add_argument('--headless')
    else:
        options.add_argument('--lang=en-GB')
        options.add_argument("accept-language=en-US")
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)

    # privacy pop-up

    xpath = "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button/span"
    driver.find_element_by_xpath(xpath).click()

    #### expand the review

    time.sleep(2)

    class_ = "ODSEW-KoToPc-ShBeI gXqMYb-hSRGPd"

    soup = BeautifulSoup(driver.page_source, "html.parser")

    #total_number_of_reviews = soup.find("div", class_="gm2-caption").text
    total_number_of_reviews = driver.find_element_by_xpath(
        '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/span[1]/span/span[1]/span[2]'
    ).text
    total_number_of_reviews = total_number_of_reviews.split(' ', 1)[0]

    ## Catch nombre d'avis
    xpath = '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/span[1]/span/span[1]/span[2]'

    review_count = driver.find_element_by_xpath(xpath).text
    review_count = review_count.split(' ', 1)[0]

    driver.find_element_by_xpath(
        '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/span[1]/span/span[1]/span[2]'
    ).click()
    #total_number_of_reviews = soup.find("div", class_="gm2-caption").text
    #a = total_number_of_reviews
    time.sleep(1)
    try :
        xpatrier = "/html/body/div[3]/div[9]/div[8]/div/div[1]/div/div/div[2]/div[7]/div[2]/button/span"
        driver.find_element_by_xpath(xpatrier).click()
    except :
        pass
    time.sleep(2)
    try :
        xpatrecent = "/html/body/div[3]/div[3]/div[1]/ul/li[2]"
        driver.find_element_by_xpath(xpatrecent).click()
    except :
        pass
    ## Catch cellule of reviews

    books_html = soup.findAll('div', class_="siAUzd-neVct")
    len(books_html)

    #scroll to show all reviews
    time.sleep(2)
    if scroll_limit:
        review_count = scroll_limit
    scrollable_div = driver.find_element_by_xpath(
        '//*[@id="pane"]/div/div[1]/div/div/div[2]')
    for i in range(0, (round(int(review_count) / 10 - 1))):
        driver.execute_script(
            'arguments[0].scrollTop = arguments[0].scrollHeight',
            scrollable_div)
        time.sleep(2)

    #Find scroll layout
    scrollable_div = driver.find_element_by_xpath(
        '//*[@id="pane"]/div/div[1]/div/div/div[2]')

    print(review_count)
    #Scroll as many times as necessary to load all reviews
    for i in range(0, (round(int(review_count / 10 - 1)))):
        driver.execute_script(
            'arguments[0].scrollTop = arguments[0].scrollHeight',
            scrollable_div)
        time.sleep(2)
    plus_list = driver.find_elements_by_link_text("Plus")
    response = BeautifulSoup(driver.page_source, 'html.parser')

    reviews = response.find_all('div',
                                class_='ODSEW-ShBeI NIyLF-haAclf gm2-body-2')

    return reviews


def get_review_summary(result_set):
    rev_dict = {'Review Rate': [], 'Review Time': [], 'Review Text': []}
    for result in result_set:

        review_rate = result.find('span',
                                  class_='ODSEW-ShBeI-H1e3jb')["aria-label"]
        review_time = result.find('span',
                                  class_='ODSEW-ShBeI-RgZmSc-date').text
        review_text = result.find('span', class_='ODSEW-ShBeI-text').text
        rev_dict['Review Rate'].append(review_rate)
        rev_dict['Review Time'].append(review_time)
        rev_dict['Review Text'].append(review_text)
    A = pd.DataFrame(rev_dict)

    A["Review Rate"] = [i.split("\xa0")[0] for i in A["Review Rate"]]
    A["Review Time"] = [i.strip("il y a ") for i in A["Review Time"]]
    A["Review Time"] = [i.replace("une", "1") for i in A["Review Time"]]
    A["Review Time"] = [i.replace("un", "1") for i in A["Review Time"]]
    return A


def get_all_gr(url, iid, name, alias):
    name
    os.path.exists(name.replace(" ", "_").replace("'", "") + ".csv")
    if os.path.exists(name.replace(" ", "_").replace("'", "") + ".csv") :
        pass
    else :
        test = get_reviews_google(url, scroll_limit=200, quiet_mode=True)
        table = get_review_summary(test)
        table["id"] = iid
        table["name"] = name
        table["alias"] = alias
        table.to_csv(name.replace(" ", "_").replace("'", "") + ".csv")
        #os.system("""gsutil cp '*.csv' 'gs://wagon-data-722-manoharan/restaurant/'""")
    return table


if __name__ == '__main__':
    #centers, radius = subzones_paris(1)
    #df = get_restaurants(centers, radius)
    #df = create_df_yelp(df)
    #df = pd.read_csv("final_resto_list.csv")
    #print(df)
    #df["id"] = df.apply(lambda x: get_place_google_id(x["name"], x["latitude"],
    #                                                  x["longitude"]),
    #                    axis=1)
    #df["lien"] = df.apply(lambda x: get_place_google_url(x["id"]), axis=1)
    #review_dates, review_rates, reviews = get_reviews_google(lien, scroll_limit=100, quiet_mode=True, return_count=False)
    #df.to_csv("restaurant_google.csv")
    df = pd.read_csv("fobokiller/data/restaurant_google.csv")

    for i in range(1,len(df)) :
        print(df["name"][i])
        try :
            test = get_all_gr(df["lien"][i],df["id"][i],df["name"][i],df["alias"][i])
        except :
            pass
