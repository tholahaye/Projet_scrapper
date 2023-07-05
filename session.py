import pymongo
import liste_url

class ScrapingSession:
    def __init__(self, url, collection_session, collection_data, list_domains, list_directories=None, limite = 10):
        self.url = url
        self.url_in_progress = None
        self.collection_session = collection_session
        self.collection_data = collection_data
        self.list_domains = list_domains
        self.list_directories = list_directories
        self.limite = limite
        self.scraped_url = 0

    def scraping_loop(self):
        while self.scraped_url < 10:
            self.scraped_url += 1
            self.select_url()
            liste_url.UrlScraper(self.url_in_progress,self.collection_session, self.collection_data, self.list_domains, self.list_directories)
            self.url_done()

    def select_url(self):
        if self.url_in_progress is None:
            self.url_in_progress = self.url
        else:
            self.url_in_progress = self.collection_session.find_one({"status": "pending"})
        url_id = self.url_in_progress["_id"]
        self.collection_session.update_one({"_id": url_id}, {"$set": {"status": "in progress"}})
        return self.url_in_progress

    def url_done(self):
        url_id = self.url_in_progress["_id"]
        self.collection_session.update_one({"_id": url_id}, {"$set": {"status": "done"}})
