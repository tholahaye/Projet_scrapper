import pymongo
import session

# Création du client MongoDB
client = pymongo.MongoClient('localhost')
# Création de la base de données
db_test = client.test_scraping
# Création de la collection_url
collection_url = db_test.url
# Création d'un index sur "url" de collection_url
collection_url.create_index([("url", pymongo.ASCENDING)])

# Création de la collection_data_session
collection_data_session = db_test.data_session
# Création d'un index sur "url" de collection_url
collection_url.create_index([("status", pymongo.ASCENDING)])

# Création de la collection_session_events
collection_session_events_test = db_test.session_events

# Création de la collection_session_domains
collection_session_domains_test = db_test.session_domains

# Création de la collection_session_dir_prefix
collection_session_dir_prefix_test = db_test.session_dir_prefix

#list_domains = ["fr.wikipedia.org", "wikimedia.org"]
#list_directories = ["/wiki/", "/w/"]
#list_directories = ["/wiki/Garnier_de_Rochefort"]

url_start = "https://fr.wikipedia.org/wiki/Garnier_de_Rochefort"
# url_start = input("URL : ")

# Définition du scope:
list_domains = ["fr.wikipedia.org", "wikimedia.org"] #  "input("domain list : ")
list_directories = ["/wiki/", "/w/"] #  input("directories list : ")




session = session.ScrapingSession(url=url_start, collection_url=collection_url,
                                  collection_session_events=collection_session_events_test,
                                  collection_data_session=collection_data_session,
                                  collection_session_domains=collection_session_domains_test,
                                  collection_session_dir_prefix=collection_session_dir_prefix_test,
                                  list_domains=list_domains, list_directories=list_directories, limit=10)
session.scraping_loop()
print("Done")
