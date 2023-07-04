import pymongo
import liste_url
from urllib.parse import urljoin, urlparse

#Création du client MongoDB
client = pymongo.MongoClient('localhost')
#Création de la base de données
db_test = client.test_scrapping_3
#Création de la collection
collection_test = db_test.scrapped_url
#Définition du scope:
list_domains = ["fr.wikipedia.org"]
list_repositories = ["/wiki/"]

url = input("URL : ")


liste_url.insert_links(url, collection_test)

