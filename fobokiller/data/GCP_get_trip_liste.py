#Biblio
import six
from google.cloud import bigquery
import sys
import csv
from selenium import webdriver
import time
import pandas as pd
import chromedriver_binary
from selenium.webdriver.chrome.options import Options
# params GCP

# Construct a BigQuery client object.
client = bigquery.Client()

PROJECT_ID = "wagon-bootcamp-328013"
table_id = "wagon-bootcamp-328013.trip.review"

job_config = bigquery.LoadJobConfig(schema=[
    bigquery.SchemaField("nom", "STRING"),
    bigquery.SchemaField("liens", "STRING"),
    bigquery.SchemaField("nb_avis", "STRING"),
    bigquery.SchemaField("type", "STRING"),
    bigquery.SchemaField("prix", "STRING")
], )
# params

url = "https://www.tripadvisor.fr/Restaurants-g187147-zfn15621628-Paris_Ile_de_France.html"

accepter = '//*[@id="onetrust-accept-btn-handler"]'
cellule = ".//a[@class='emrzT Vt o'"
limite = '//*[@id="secondaryText"]'
# Import the webdriver
driver = driver = webdriver.Firefox()
driver.get(url)


# Privacy pop-up

time.sleep(5)
driver.find_element_by_xpath(accepter).click()
time.sleep(5)
try :
    driver.find_element_by_xpath(limite).click()
    print("Option limitation de recherche activer")
    time.sleep(5)
except :
    print("Option limitation de recherche indisponible")
container = driver.find_elements_by_xpath(".//div[@class='cauvp Gi o']")

nom_restaurant = []
nb_avis = []
type_der = []
cout = []
lien = []


for i in range(0, 50,1):
    for j in range(len(container)):
        try:
            temp_nom_restaurant = container[j].find_element_by_xpath(
                ".//a[@class='bHGqj Cj b']").text
            temp_nom_restaurant = temp_nom_restaurant.replace(",",".")
            print(temp_nom_restaurant.split(".")[1])
            temp_nom_restaurant = temp_nom_restaurant.split(".")[1]
            nom_restaurant.append(temp_nom_restaurant)
        except:
            temp_nom_restaurant = "Failed"
            nom_restaurant.append(temp_nom_restaurant)
        try:
            temp_lien = container[j].find_element_by_xpath(
                ".//a[@class='bHGqj Cj b']").get_attribute('href')
            lien.append(temp_lien)
        except:
            temp_lien = "Failed"
            lien.append(temp_lien)
        try:
            temp_nb_avis = container[j].find_element_by_xpath(
                ".//span[@class='NoCoR']").text
            nb_avis.append(temp_nb_avis)
        except:
            temp_nb_avis = "Failed"
            nb_avis.append(temp_nb_avis)
        try:
            l = container[j].find_element_by_xpath(".//span[@class='XNMDG']")
            if len(l) > 0:
                temp_type_der = l.text
                type_der.append(temp_type_der)
            else :
                type_der.append("Failed")
        except:
            temp_type_der("Failed")
            type_der.append(temp_type_der)
        try:
            temp_cout = container[j].find_element_by_xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div[2]/div[3]/div[2]/div/div[5]/div[3]/div[5]/div[1]/div/div/div[15]/span/div[1]/div[2]/div[2]/div/div[2]/span[2]/span'
            ).text
            cout.append(temp_cout)
        except:
            temp_cout = "Failed"
            cout.append("temp_cout")
        try:
            print(container[j].find_element_by_xpath(
                ".//a[@class='bHGqj Cj b']").text)
        except:
            print("Failed")

        push_p = ",".join([
            temp_nom_restaurant, temp_lien, temp_nb_avis, temp_type_der.replace(",","-"),
            temp_cout
        ])
        print(push_p)
        body = six.BytesIO(bytes(push_p, 'utf-8'))
        client.load_table_from_file(body, table_id,
                                    job_config=job_config).result()
    try:
        driver.find_element_by_link_text(str(i + 2)).click()
        time.sleep(3)
        print("page suivante" + str(i + 2))
        time.sleep(3)
        container = driver.find_elements_by_xpath(
            ".//div[@class='cauvp Gi o']")
    except:
        print(driver.find_elements_by_xpath(".//div[@class='cauvp Gi o']"))
        time.sleep(10)
        break

        #container = driver.find_elements_by_xpath(
        #    ".//div[@class='cauvp Gi o']")

temp = zip(nom_restaurant, lien, nb_avis, type_der, cout)

liste = pd.DataFrame(temp)

liste.rename(columns={
    0: "nom",
    1: "lien",
    2: "nb_avis",
    3: "type",
    4: "prix",
},
             inplace=True)

liste.to_csv("Paris1.csv", sep=",")
