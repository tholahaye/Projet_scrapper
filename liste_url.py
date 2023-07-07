import requests
import bs4
from urllib.parse import urljoin, urlparse
import traceback
import time
import socket
from datetime import datetime
from urllib.parse import urljoin, urlparse
import pickle
import bs4
import requests


class UrlScraper:
    def __init__(self, url, collection_url, collection_session_events,
                 collection_data_session, id_session, list_domains, list_directories=None):
        self.url = url
        self.collection_url = collection_url
        self.collection_session_events = collection_session_events
        self.collection_data_session = collection_data_session
        self.id_session = id_session
        self.list_domains = list_domains
        self.list_directories = list_directories
        self.links_with_text = set()
        self.host_name = socket.gethostname()
        self.cookies = self._get_cookies()
        # Requête HTTP sur la page cible
        self.error = False
        self.request = self._url_request()

        self.inserted_links_cpt = 0
        if self.request is not None:
            self.soup = bs4.BeautifulSoup(self.request.content, 'html.parser')

    def _url_request(self):
        self.collection_session_events.insert_one({"idSession": self.id_session,
                                                   "url": self.url,
                                                   "machine_ID": self.host_name,
                                                   "dateEvent": datetime.now(),
                                                   "eventType": "launch url scraping",
                                                   "eventMessage": f"launch scraping "
                                                                   f"on {self.url}"})
        for nb_requests in range(11):
            if nb_requests > 0:
                time.sleep(60)
            if nb_requests == 10:
                self.error = True
                self.collection_session_events.insert_one({"idSession": self.id_session,
                                                           "url": self.url,
                                                           "machine_ID": self.host_name,
                                                           "dateEvent": datetime.now(),
                                                           "eventType": "url scraping abortion",
                                                           "eventMessage": f"{nb_requests} "
                                                                           f"tentatives have "
                                                                           f"failed "
                                                                           f"to scrap {self.url}, "
                                                                           f"request "
                                                                           f"abortion"})
                break
            try:

                result = requests.get(self.url, cookies=self.cookies)

            except requests.ConnectionError:
                print("Erreur de connection")
                self.collection_session_events.insert_one({"idSession": self.id_session,
                                                           "url": self.url,
                                                           "machine_ID": self.host_name,
                                                           "dateEvent": datetime.now(),
                                                           "eventType": "url scraping error",
                                                           "eventMessage": f"Connection error "
                                                                           f"when scraping "
                                                                           f"{self.url} "
                                                                           f"after "
                                                                           f"{nb_requests+1} "
                                                                           f"attempt(s)"})
                continue
            except requests.Timeout:
                print("La requête prend trop de temps.")
                self.collection_session_events.insert_one({"idSession": self.id_session,
                                                           "url": self.url,
                                                           "machine_ID": self.host_name,
                                                           "dateEvent": datetime.now(),
                                                           "eventType": "url scraping error",
                                                           "eventMessage": f"Time out event "
                                                                           f"when scraping "
                                                                           f"{self.url} "
                                                                           f"after "
                                                                           f"{nb_requests + 1} "
                                                                           f"attempt(s)"})
                continue
            except requests.TooManyRedirects:
                print("La requête excède la limite de redirection.")
                self.error = True
                self.collection_session_events.insert_one({"idSession": self.id_session,
                                                           "url": self.url,
                                                           "machine_ID": self.host_name,
                                                           "dateEvent": datetime.now(),
                                                           "eventType": "url scraping abortion",
                                                           "eventMessage": f"Too many redirections"
                                                                           f" when scraping "
                                                                           f"{self.url}, "
                                                                           f"request abortion"})
                break
            except Exception:
                print(traceback.format_exc())
                self.error = True
                self.collection_session_events.insert_one({"idSession": self.id_session,
                                                           "url": self.url,
                                                           "machine_ID": self.host_name,
                                                           "dateEvent": datetime.now(),
                                                           "eventType": "url scraping abortion",
                                                           "eventMessage":
                                                               f"{traceback.format_exc()} "
                                                               f"when scraping "
                                                               f"{self.url}, "
                                                               f"request abortion"})
                break
            if result.status_code == 200:
                # Ajout des cookies à data_session
                pickle_cookies = pickle.dumps(result.cookies)
                self.collection_data_session.update_one({"_id": self.id_session},
                                                        {"$set": {"cookies": pickle_cookies}})
                self.cookies = self._get_cookies()
                return result
            print(result.status_code)
            self.collection_session_events.insert_one({"idSession": self.id_session,
                                                       "url": self.url,
                                                       "machine_ID": self.host_name,
                                                       "dateEvent": datetime.now(),
                                                       "eventType": "url scraping error",
                                                       "eventMessage": f"{result.status_code} "
                                                                       f"returned when scraping "
                                                                       f"{self.url} after "
                                                                       f"{nb_requests + 1} attempt(s)"})

    def _get_cookies(self):
        result = None
        query = self.collection_data_session.find_one({"_id": self.id_session})
        try:
            result = pickle.loads(query["cookies"])
        except KeyError:
            pass
        return result

    def _check_domain(self, link):
        parsed_url = urlparse(link)
        for domain in self.list_domains:
            if parsed_url.netloc.endswith(domain):
                return True
        return False

    def _check_directory(self, link):
        parsed_url = urlparse(link)
        for directory in self.list_directories:
            if parsed_url.path.startswith(directory):
                return True
        return False

    def _check_scope(self, link):
        if self._check_domain(link):
            if len(self.list_directories) == 0:
                return True
            if self._check_directory(link):
                return True
        print(f"{link} est hors du scope")
        return False

    def _absolute_links(self, soup):
        for a in soup.findAll('a'):
            if a.get('href'):
                href = a['href']
                absolute_url = urljoin(self.url, href)
                a['href'] = absolute_url
                if absolute_url not in self.links_with_text:
                    self.links_with_text.add(absolute_url)
        return self.links_with_text

    # Fonction qui renvoit True si l'url est déjà dans la collection cible, False sinon.
    def _inserted_urls(self, link):
        if self.collection_url.find_one({"url": link}) is not None:
            print(f"{link} déja dans la base")
            return True
        return False

    def insert_links(self):
        if self.request is not None:

            for link in self._absolute_links(self.soup):
                if self.list_directories is None:
                    self.list_directories = []
                if self._check_scope(link):
                    if not self._inserted_urls(link):
                        self.collection_url.insert_one({"url": f"{link}", "status": "pending",
                                                        "id_session": self.id_session})
                        self.inserted_links_cpt += 1
                        print(f"Bien inséré à la db :{link}")

    def _textscrap(self):
        h1 = []
        h2 = []
        titre = []
        b = []
        strong = []
        em = []
        for text in self.soup.findAll('title'):
            titre.append(text.text)
        for text in self.soup.findAll('h1'):
            h1.append(text.text)
        for text in self.soup.findAll('h2'):
            h2.append(text.text)
        for text in self.soup.findAll(['b']):
            b.append(text.text)
        for text in self.soup.findAll(['strong']):
            strong.append(text.text)
        for text in self.soup.findAll(['em']):
            em.append(text.text)

        return{"html": str(self.soup.prettify),
               "metadata": {
                   "titles": {"title": titre, "h1": h1, "h2": h2},
                   "emphasises": {"b": b, "strong": strong, "em": em}
               }}

    def insert_data(self):
        if self.request is not None:

            parsed = self._textscrap()
            document = {"html": parsed["html"],
                        "metadata": parsed["metadata"]}

            self.collection_url.update_one({"url": self.url, "id_session": self.id_session},
                                           {"$set": {"data": document}})
            self.collection_session_events.insert_one({"idSession": self.id_session,
                                                       "url": self.url,
                                                       "machine_ID": self.host_name,
                                                       "dateEvent": datetime.now(),
                                                       "eventType": "url scraping completion",
                                                       "eventMessage": f"scraping on {self.url} completed, "
                                                                       f"data inserted and addition of "
                                                                       f"{self.inserted_links_cpt} new links"})
