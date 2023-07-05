import pymongo
import liste_url

class ScrapingSession:
    def __init__(self, url, collection_session_ip, collection_data, list_domains, list_directories=None, limite = 10):
        self.url = url
        self.url_in_progress = None
        self.collection_session = collection_session_ip
        self.collection_data = collection_data
        self.list_domains = list_domains
        self.list_directories = list_directories
        self.limite = limite
        self.scraped_url = 0

    def scraping_loop(self):
        while self.scraped_url < 10:
            self.scraped_url += 1

            pass

    def select_url(self):
        if self.url_in_progress is None:
            self.url_in_progress = self.url
        #selected_url = self.collection_session.find_one({"status": "pending"})
        #selected_url.update_one(selected_url, {"status": "in progress"})
        return self.url_in_progress

    def url_done(self):
        pass
