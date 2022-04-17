#Biblio

import sys
import csv
from webbrowser import get
from selenium import webdriver
import time
import pandas as pd

accepter = '//*[@id="onetrust-accept-btn-handler"]'
cellule = ".//a[@class='emrzT Vt o'"
limite = '//*[@id="secondaryText"]'
adresse_postal = "/html/body/div[2]/div[1]/div/div[3]/div/div/div[3]/span[1]/span/a"



def get_adress(url2):
    driver2 = webdriver.Firefox()
    driver2.get(url2)
    time.sleep(3)
    driver2.find_element_by_xpath(accepter).click()
    gaddress = driver2.find_element_by_xpath(adresse_postal).text
    driver2.close()
    return gaddress


def get_trip_liste(url,files_names) :


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
    adresse= []
    for i in range(0, 410,1):
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
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div[2]/div[3]/div[2]/div/div[5]/div[3]/div[5]/div[1]/div/div/div[15]/span/div[1]/div[2]/div[2]/div/div[2]/span[2]/span'
                ).text)
            except:
                cout.append("Failed")
            try :
                adresse.append(
                    get_adress(container[j].find_element_by_xpath(
                        ".//a[@class='bHGqj Cj b']").get_attribute('href')))
            except :
                adresse.append("Failed")
            try:
                print(container[j].find_element_by_xpath(
                    ".//a[@class='bHGqj Cj b']").text)
            except:
                print("Failed")

        try:
            driver.find_element_by_link_text(str(i + 2)).click()
            time.sleep(3)
            print("page suivante" + str(i + 2))
            time.sleep(3)
            container = driver.find_elements_by_xpath(
                ".//div[@class='cauvp Gi o']")
        except:
            #print(driver.find_elements_by_xpath(".//div[@class='cauvp Gi o']"))
            print(
                "======================== Derniere page ========================"
            )
            time.sleep(10)
            break

            #container = driver.find_elements_by_xpath(
            #    ".//div[@class='cauvp Gi o']")

    temp = zip(nom_restaurant, lien, nb_avis, type_der, cout, adresse)

    liste = pd.DataFrame(temp)

    liste.rename(columns={
        0: "nom",
        1: "lien",
        2: "nb_avis",
        3: "type",
        4: "prix",
    },
                inplace=True)

    liste.to_csv(files_names, sep=",")


liste = pd.read_csv("scrap_list.csv")




# params
#5 eme
#url = "https://www.tripadvisor.fr/Restaurants-g187147-zfn15621638-Paris_Ile_de_France.html"
#6eme
#url= "https://www.tripadvisor.fr/Restaurants-g187147-zfn15621634-Paris_Ile_de_France.html"
#7eme
#url = "https://www.tripadvisor.fr/Restaurants-g187147-zfn15621644-Paris_Ile_de_France.html"
#8eme




test = pd.read_csv("scrap_list.csv", sep=";")


for i in range(16,len(test)) :
    get_trip_liste(test["Liens"][i],test["Paris"][i])
