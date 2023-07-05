import pymongo
import liste_url
from urllib.parse import urljoin, urlparse

#Création du client MongoDB
client = pymongo.MongoClient('localhost')
#Création de la base de données
db_test = client.test_scrapping
#Création de la collection_session
collection_session_test = db_test.url_list
#Création de la collection_data
collection_data_test = db_test.url_data
#Définition du scope:
list_domains = ["fr.wikipedia.org"]
list_directories = ["/wiki/"]

url ="https://fr.wikipedia.org/wiki/Garnier_de_Rochefort" #input("URL : ")


scrapper = liste_url.UrlScrapper(url, collection_session_test, collection_data_test, list_domains, list_directories)
scrapper.insert_links()
scrapper.insert_document()
print("Done")
