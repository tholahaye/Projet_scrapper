import pymongo
import session

#Création du client MongoDB
client = pymongo.MongoClient('localhost')
#Création de la base de données
db_test = client.test_scraping
#Création de la collection_session
collection_session_test = db_test.url_list
# Création de la collection_session_url_events
collection_session_url_events_test = db_test.session_url_events
#Création de la collection_data
collection_data_test = db_test.url_data
#Définition du scope:
list_domains = ["fr.wikipedia.org", "wikimedia.org"]
list_directories = ["/wiki/","/w/"]

url_start ="https://fr.wikipedia.org/wiki/Garnier_de_Rochefort" #input("URL : ")


session = session.ScrapingSession(url=url_start, collection_session=collection_session_test,
                                  collection_data=collection_data_test,
                                  collection_session_url_events=collection_session_url_events_test,
                                  list_domains=list_domains, list_directories=list_directories)
session.scraping_loop()
print("Done")
