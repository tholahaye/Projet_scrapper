import socket
from datetime import datetime
import sys
import liste_url


class ScrapingSession:
    def __init__(self, url, collection_url, collection_session_events, collection_data_session,
                 collection_session_domains, collection_session_dir_prefix,
                 list_domains, list_directories=None, limit=2):
        self.url = url
        self.url_in_progress = "init"
        self.collection_url = collection_url
        self.collection_session_events = collection_session_events
        self.collection_data_session = collection_data_session
        self.collection_session_domains = collection_session_domains
        self.collection_session_dir_prefix = collection_session_dir_prefix
        self.list_domains = list_domains
        self.list_directories = list_directories
        self.limit = limit
        self.host_name = socket.gethostname()
        if not self.check_list_domains_empty():
            print("Erreur: la liste de domaines est vide.")
            sys.exit()

        self.session_log("start")
        query = self.collection_data_session.find_one({"start_url": self.url,
                                                       "status": "in progress"})

        self.id_session = query["_id"]
        self.collection_url.insert_one({"url": f"{self.url}",
                                        "status": "pending",
                                        "start_datetime": datetime.now(),
                                        "id_session": self.id_session})
        # Insertion du log de demarrage de la session
        self.collection_session_events.insert_one({"id_session": self.id_session,
                                                   "machine_ID": self.host_name,
                                                   "datetime": datetime.now(),
                                                   "event_type": "Session starting"})
        # writing of the domains in the database
        for domain in self.list_domains:
            self.collection_session_domains.insert_one({"id_session": self.id_session,
                                                        "domain": domain})
        # writing of the directory prefixes in the database
        if len(self.list_directories) > 0:
            for dir_prefix in self.list_directories:
                self.collection_session_dir_prefix.insert_one({"id_session": self.id_session,
                                                               "dir_prefix": dir_prefix}),

    def check_list_domains_empty(self):
        if self.list_domains is not None:
            for domain in self.list_domains:
                if domain != "":
                    return True
        return False

    def session_log(self, status):
        if status == "start":
            self.collection_data_session.insert_one({"start_url": self.url,
                                                     "start_datetime": datetime.now(),
                                                     "status": "in progress"})
        if status == "completed":
            self.collection_data_session.update_one({"_id": self.id_session},
                                                    {"$set": {"status": "completed",
                                                              "end_datetime": datetime.now()}})
            print("Session completed")
        if status == "errors":
            self.collection_data_session.update_one({"_id": self.id_session},
                                                    {"$set": {"status": "terminated with error(s)",
                                                              "end_datetime": datetime.now()}})
            print("Session terminated with error(s)")
        if status == "interrupted":
            self.collection_data_session.update_one({"_id": self.id_session},
                                                    {"$set": {"status": "pause"}})
            print("Machine exit: the limit has been reached")

    def scraping_loop(self):

        for number in range(self.limit):
            self.select_url()
            if self.url_in_progress == "None":
                break

            scraper = liste_url.UrlScraper(url=self.url_in_progress,
                                           collection_url=self.collection_url,
                                           collection_session_events=self.collection_session_events,
                                           collection_data_session=self.collection_data_session,
                                           id_session=self.id_session,
                                           list_domains=self.list_domains, list_directories=self.list_directories)


            if scraper.error:
                print(f"{self.url_in_progress} aborted wit an error")
                self.url_error()
            else:
                scraper.insert_links()
                scraper.insert_data()
                print(f"{self.url_in_progress} is done")
                self.url_done()

        query_in_progress = self.collection_url.find_one({"status": "in progress",
                                                          "id_session": self.id_session})
        query_pending = self.collection_url.find_one({"status": "pending",
                                                      "id_session": self.id_session})
        query_error = self.collection_url.find_one({"status": "error",
                                                    "id_session": self.id_session})
        if query_in_progress is None:
            if query_pending is None:
                if query_error is None:
                    self.session_log("completed")
                else:
                    self.session_log("errors")
            else:
                self.session_log("interrupted")

    def select_url(self):
        if self.url_in_progress == "init":
            self.url_in_progress = self.url

        else:
            query = self.collection_url.find_one({"status": "pending",
                                                  "id_session": self.id_session})
            if query is not None:
                self.url_in_progress = query["url"]
                url_id = self.collection_url.find_one({"url": self.url_in_progress})["_id"]
                self.collection_url.update_one({"_id": url_id}, {"$set": {"status": "in progress",
                                                                          "start_datetime": datetime.now()}})
            else:
                self.url_in_progress = "None"




    def url_done(self):
        url_id = self.collection_url.find_one({"url": self.url_in_progress})["_id"]
        self.collection_url.update_one({"_id": url_id}, {"$set": {"status": "done"}})

    def url_error(self):
        url_id = self.collection_url.find_one({"url": self.url_in_progress})["_id"]
        print(url_id)
        self.collection_url.update_one({"_id": url_id}, {"$set": {"status": "error"}})
