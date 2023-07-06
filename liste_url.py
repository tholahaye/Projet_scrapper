import requests
import bs4
from urllib.parse import urljoin, urlparse
import traceback
import time
import socket
from datetime import datetime


class UrlScraper:
    def __init__(self, url, collection_url, collection_data, collection_session_events,
                 id_session, list_domains, list_directories=None):
        self.url = url
        self.collection_url = collection_url
        self.collection_data = collection_data
        self.collection_session_events = collection_session_events
        self.id_session = id_session
        self.list_domains = list_domains
        self.list_directories = list_directories
        self.links_with_text = set()
        self.request = self._url_request()
        self.host_name = socket.gethostname()
        if self.request is not None:
            self.soup = bs4.BeautifulSoup(self.request.content, 'html.parser')

        # Requête HTTP sur la page cible
    def _url_request(self):
        self.collection_session_events.insert_one({"idSession": self.id_session,
                                                       "url": self.url,
                                                       #"machineID": self.host_name,
                                                       "dateEvent": datetime.now(),
                                                       "eventType": "launch",
                                                       "eventMessage": f"launch scraping on {self.url}"})
        result = None
        for nb_requests in range(10):
            if nb_requests > 0:
                time.sleep(60)
            try:
                result = requests.get(self.url)
            except requests.ConnectionError:
                print("Erreur de connection")
                continue
            except requests.Timeout:
                print("La requête prend trop de temps.")
                continue
            except requests.TooManyRedirects:
                print("La requête excède la limite de redirection.")
                break
            except Exception:
                print(traceback.format_exc())
                break
            if result.status_code == 200:
                # log de réussite de connection qui contient l'id_session les cookies
                return result
            print(result.status_code)
            # Ajout du log de l'erreur ?

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

    def insert_document(self):
        if self.request is not None:

            parsed = self._textscrap()
            document = {"url": self.url, "html": parsed["html"],
                        "metadata": parsed["metadata"], "id_session": self.id_session}

            self.collection_data.insert_one(document)
