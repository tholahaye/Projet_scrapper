import pymongo
import liste_url

#Création du client MongoDB
client = pymongo.MongoClient('localhost')
#Création de la base de données
db_test = client.test_scraping
#Création de la collection_session
collection_session_test = db_test.url_list
#Création de la collection_data
collection_data_test = db_test.url_data
#Définition du scope:
list_domains = ["fr.wikipedia.org", "wikimedia.org"]
list_directories = ["/wiki/","/w/"]

url ="https://fr.wikipedia.org/wiki/Garnier_de_Rochefort" #input("URL : ")


scraper = liste_url.UrlScraper(url, collection_session_test, collection_data_test, list_domains, list_directories)
scraper.insert_links()
scraper.insert_document()
print("Done")
