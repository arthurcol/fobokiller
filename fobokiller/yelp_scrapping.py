import pandas as pd
import numpy as np
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv
import os

path = find_dotenv()
load_dotenv(path)
yelp_key = os.getenv('YELP_KEY')

path_list_rest = os.path.join(os.path.dirname(__file__),'data/final_resto_list.csv')
path_data = os.path.join(os.path.dirname(__file__),'data/scrapping.csv')

list_resto = pd.read_csv(path_list_rest,index_col=0).reset_index()
list_resto=list_resto[list_resto['review_count']>20]
list_resto.reset_index(drop=True, inplace=True)


try:
    dt = pd.read_csv(path_data, index_col=0)
    previous_scrap = list(dt['alias'].unique())
except:
    previous_scrap = []
    print('No previous scrapping')


def get_reviews_yelp(url,alias, verbose=0, quiet_mode=True, load_strategy='eager'):

    #pages

    options = Options()
    if quiet_mode:
        options.add_argument('--headless')
    options.page_load_strategy = load_strategy
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    xpath_page = "//yelp-react-root/div[1]/div[4]/div/div/div[2]/div/div[1]/div[2]/section/div[2]/div/div[4]/div[2]/span"
    try:
        page = driver.find_element(By.XPATH, xpath_page).text
        n_pages = int(page.split('of ')[1])

    except:
        n_pages = 1

    reviews = []
    rates = []
    dates = []
    aliases = []

    a_toappend = alias

    print(f'### {n_pages} pages to scrap for {a_toappend}###')

    for n in range(n_pages):

        if verbose > 0:
            print(f'--- Fetching reviews of page #{n+1}...')

        #url of the n_page
        url_ = f'{url}?start={n*10}'
        driver.get(url_)
        xpath_all_review = f"//yelp-react-root/div[1]/div[4]/div/div/div[2]/div/div[1]/div[2]/section/div[2]/div/ul"

        try:
            review_block = driver.find_element(By.XPATH, xpath_all_review)
        except:
            continue
        try:
            all_reviews = review_block.find_elements(By.TAG_NAME, 'li')
        except:
            continue
        for i, r in enumerate(all_reviews):
            aliases.append(a_toappend)
            if verbose > 1:
                print(f'--Getting reviews #{i+1}...')
            reviews.append(r.text)
            try:
                rate = r.find_element(By.XPATH,
                                      './/div/div[2]/div/div[1]/span/div')
                rates.append(rate.get_attribute('aria-label'))
            except:
                rates.append('NAN')
            try:
                dates.append(
                    r.find_element(By.XPATH,
                                   './/div/div[2]/div/div[2]/span').text)
            except:
                dates.append('NAN')

    return aliases, dates, rates, reviews

def save_data(alias,dates,rates,reviews):
    df = pd.DataFrame({'alias':alias,
                       'date':dates,
                       'rate':rates,
                       'review':reviews
                           })
    scrapping_df = pd.read_csv(path_data,index_col=0)
    scrapping_df = scrapping_df.append(df,ignore_index=True)
    return scrapping_df

if __name__ == "__main__":
    if previous_scrap == []:
        pd.DataFrame(columns=['alias', 'date', 'rate', 'review']).to_csv(
            path_data)
    for i in range(len(list_resto)):
        if list_resto.loc[i, 'alias'] not in previous_scrap:
            alias, dates, rates, reviews = get_reviews_yelp(
                list_resto.loc[i, 'url'], list_resto.loc[i, 'alias'],verbose=1)
            tmp = save_data(alias, dates, rates, reviews)
            tmp.to_csv(path_data)
            print(list_resto.loc[i, 'alias'], 'scrapped and saved')
        else:
            print(list_resto.loc[i, 'alias'],'already scrapped')
