import pymongo
import liste_url

#Création du client MongoDB
client = pymongo.MongoClient('localhost')
#Création de la base de données
db_test = client.test_scrapping_3
#Création de la collection
collection_test = db_test.scrapped_url

url = input("URL : ")

liste_url.insert_links(url, collection_test)
