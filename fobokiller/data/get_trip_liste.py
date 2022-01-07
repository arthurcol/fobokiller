#Biblio

import sys
import csv
from selenium import webdriver
import time
import pandas as pd
import chromedriver_binary
from selenium.webdriver.chrome.options import Options

# params

url = "https://www.tripadvisor.fr/Restaurants-g187147-Paris_Ile_de_France.html"

accepter = '//*[@id="onetrust-accept-btn-handler"]'
cellule = ".//a[@class='emrzT Vt o'"
# Import the webdriver
driver = driver = webdriver.Firefox()
driver.get(url)

# Privacy pop-up

time.sleep(5)
driver.find_element_by_xpath(accepter).click()

container = driver.find_elements_by_xpath(".//div[@class='cauvp Gi o']")

nom_restaurant = []
nb_avis = []
type_der = []
cout = []
lien = []

for i in range(0, 410):
    for j in range(len(container)):
        try:
            nom_restaurant.append(container[j].find_element_by_xpath(
                ".//a[@class='bHGqj Cj b']").text)
        except:
            nom_restaurant.append("Failed")
        try:
            lien.append(container[j].find_element_by_xpath(
                ".//a[@class='bHGqj Cj b']").get_attribute('href'))
        except:
            lien.append("Failed")
        try:
            nb_avis.append(container[j].find_element_by_xpath(
                ".//span[@class='NoCoR']").text)
        except:
            nb_avis.append("Failed")
        try:
            type_der.append(container[j].find_element_by_xpath(
                ".//span[@class='XNMDG']").text)
        except:
            type_der.append("Failed")
        try:
            cout.append(container[j].find_element_by_xpath(
                ".//span[@class='XNMDG']").text)
        except:
            cout.append("Failed")
        try:
            print(container[j].find_element_by_xpath(
                ".//a[@class='bHGqj Cj b']").text)
        except:
            print("Failed")
    driver.find_element_by_link_text(str(i + 2)).click()
    try:
        time.sleep(3)
        print("page suivante" + str(i + 2))
        time.sleep(3)
        container = driver.find_elements_by_xpath(
            ".//div[@class='cauvp Gi o']")
    except:
        print("add time")
        time.sleep(10)

        container = driver.find_elements_by_xpath(
            ".//div[@class='cauvp Gi o']")

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

liste.to_csv("LISTE20K.csv", sep=",")
