import liste_url
import socket
from datetime import datetime
import sys


class ScrapingSession:
    def __init__(self, url, collection_url, collection_data, collection_session_events, collection_data_session,
                 list_domains, list_directories=None, limite=2):
        self.url = url
        self.url_in_progress = None
        self.collection_url = collection_url
        self.collection_data = collection_data
        self.collection_session_events = collection_session_events
        self.collection_data_session = collection_data_session
        self.list_domains = list_domains
        self.list_directories = list_directories
        self.limite = limite
        self.scraped_url = 0
        self.host_name = socket.gethostname()
        if not self.check_list_domains_empty():
            print("Erreur: la liste de domaines est vide.")
            sys.exit()
        self.session_log("start")
        query = self.collection_data_session.find_one({"start_url": self.url, "status": "in progress"})

        self.id_session = query["_id"]
        self.collection_url.insert_one({"url_de_la_page": f"{self.url}",
                                            "url_du_lien": f"{self.url}", "status": "pending",
                                        "id_session": self.id_session})
        # Insertion du log de demarrage de la session
        self.collection_session_events.insert_one({"id_session": self.id_session, "machine_ID": self.host_name,
                                                   "datetime": datetime.now(), "event_type": "Session starting"})

    def check_list_domains_empty(self):
        if self.list_domains is not None:
            for domain in self.list_domains:
                if domain != "":
                    return True
        return False
    def session_log(self, status):
        if status == "start":
            self.collection_data_session.insert_one({"start_url": self.url,
                                                     "start_datetime": datetime.now(), "status": "in progress"})
        if status == "done":
            self.collection_data_session.update_one({"_id": self.id_session}, {"$set": {"status": "done"}})

    def scraping_loop(self):

        for n in range(self.limite):
            self.scraped_url += 1
            self.select_url()
            scraper = liste_url.UrlScraper(url=self.url_in_progress, collection_url=self.collection_url,
                                           collection_data=self.collection_data,
                                           collection_session_events=self.collection_session_events,
                                           id_session=self.id_session,
                                           list_domains=self.list_domains, list_directories=self.list_directories)
            scraper.insert_links()
            scraper.insert_document()
            print(f"{self.url_in_progress} is done")
            self.url_done()
        self.session_log("done")
        print("Loop completed")

    def select_url(self):
        if self.url_in_progress is None:
            self.url_in_progress = self.url

        else:
            query = self.collection_url.find_one({"status": "pending"})
            self.url_in_progress = query["url_du_lien"]
            print(self.url_in_progress)
        url_id = self.collection_url.find_one({"url_du_lien": self.url_in_progress})["_id"]
        self.collection_url.update_one({"_id": url_id}, {"$set": {"status": "in progress"}})
        return self.url_in_progress

    def url_done(self):
        url_id = self.collection_url.find_one({"url_du_lien": self.url_in_progress})["_id"]
        self.collection_url.update_one({"_id": url_id}, {"$set": {"status": "done"}})
