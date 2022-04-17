#Biblio

import sys
import csv
from selenium import webdriver
import time
import locale
import datetime

# define env lang

locale.setlocale(locale.LC_ALL, 'fr_FR')
# Params Xpath

# bouton accepter

accepter = '//*[@id="onetrust-accept-btn-handler"]'
address = "/html/body/div[2]/div[1]/div/div[3]/div/div/div[3]/span[1]/span/a"
# Afficher commentaire en entier
expandr = "//span[@class='taLnk ulBlueLinks']"
cellule = ".//div[@class='review-container']"
nb_avis = "eBTWs"



def get_adress(url):
    driver2 = webdriver.Firefox()
    driver2.get(url)
    time.sleep(3)
    driver2.find_element_by_xpath(accepter).click()
    gaddress = driver2.find_element_by_xpath(adresse_postal).text
    driver2.close()
    return gaddress


def Scrap_ta(url,name):
    # default path to file to store data
    path_to_file = "/Users/nicolasmanoharan/code/nicolasmanoharan/fobokiller/fobokiller/data/Paris2_TA.csv"

    # default number of scraped pages
    num_page = 4500

    # default tripadvisor website of restaurant
    #url ="https://www.tripadvisor.fr/Restaurant_Review-g187130-d2258927-Reviews-Casse_Cailloux-Tours_Indre_et_Loire_Centre_Val_de_Loire.html"
    #url = "https://www.tripadvisor.fr/Hotel_Review-g187127-d2037067-Reviews-Pierre_Vacances_Residence_Le_Moulin_des_Cordeliers-Loches_Indre_et_Loire_Centre_Val_de.html"
    # if you pass the inputs in the command line
    if (len(sys.argv) == 4):
        path_to_file = sys.argv[1]
        num_page = int(sys.argv[2])
        url = sys.argv[3]

    # Import the webdriver
    driver = webdriver.Firefox()
    driver.get(url)

    # Open the file to save the review
    csvFile = open(path_to_file, 'a', encoding="utf-8")
    csvWriter = csv.writer(csvFile)
    time.sleep(5)
    driver.find_element_by_xpath(accepter).click()

    adresse = driver.find_element_by_xpath(address).text
    nb_avis = driver.find_element_by_xpath(
        "/html/body/div[2]/div[2]/div[2]/div[6]/div/div[1]/div[4]/div/div[1]/div/div[1]/span"
    ).text
    nb_avis = "".join(nb_avis.split())
    nb_avis = nb_avis.replace("(", "")
    nb_avis = nb_avis.replace(")", "")
    num_page = int(nb_avis) // 10

    # change the value inside the range to save more or less reviews
    for i in range(0, num_page):
        print(i)
        # expand the review
        time.sleep(2)
        try:
            driver.find_element_by_xpath(expandr).click()
        except:
            print(None)

        container = driver.find_elements_by_xpath(cellule)

        for j in range(len(container)):

            title = container[j].find_element_by_xpath(
                ".//span[@class='noQuotes']").text
            date = container[j].find_element_by_xpath(
                ".//span[contains(@class, 'ratingDate')]").get_attribute(
                    "title")
            rating = container[j].find_element_by_xpath(
                ".//span[contains(@class, 'ui_bubble_rating bubble_')]"
            ).get_attribute("class").split("_")[3]
            review = container[j].find_element_by_xpath(
                ".//p[@class='partial_entry']").text.replace("\n", " ")
            date = datetime.datetime.strptime(date, "%d %B %Y").strftime("%d/%m/%Y")
            csvWriter.writerow([date, float(rating)/10, title, review, adresse,name])
        # change the page
        try:
            driver.find_element_by_xpath(
                './/a[@class="nav next ui_button primary"]').click()
        except:
            driver.close()
            return



#####


####
import pandas as pd

test = pd.read_csv(
    "/Users/nicolasmanoharan/code/nicolasmanoharan/fobokiller/fobokiller/data/Paris2.csv"
)

for i in range(1,test.shape[0]) :
    if test["nom"][i] != "Failed" :
        try :
            Scrap_ta(test["lien"][i],test["nom"][i])
        except :
            None


#[Scrap_ta(i,j) for i in test["lien"] for j in test["nom"]]
