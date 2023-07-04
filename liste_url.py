import requests
import bs4
from urllib.parse import urljoin, urlparse
import traceback

class ScrappingSession:
    def __init__(self, url,collection, list_domains, list_repositories=None, limite=None):
        self.url = url
        self.collection = collection
        self.list_domains = list_domains
        self.list_repositories = list_repositories
        self.limite = limite
        self.links_with_text = []
    def check_domain(self):
        parsed_url = urlparse(self.url)
        for domain in self.list_domains:
            if parsed_url.netloc.endswith(domain):
                return True
        return False

    def check_repository(self):
        parsed_url = urlparse(self.url)
        for repository in self.list_repositories:
            if parsed_url.path.startswith(repository):
                return True
        return False

    def check_scope(self):
        if self.check_domain():
            if len(self.list_repositories) == 0:
                return True
            if self.check_repository():
                return True
        print(f"{self.url} est hors du scope")
        return False

    # Requête HTTP sur la page cible
    def url_request(self):
        result = None
        nb_requests = 0
        while nb_requests < 10:
            try:
                result = requests.get(self.url)
            except requests.ConnectionError:
                print("Erreur de connection")
                nb_requests += 1
            except requests.Timeout:
                print("La requête prend trop de temps.")
                nb_requests += 1
            except requests.TooManyRedirects:
                print("La requête excède la limite de redirection.")
                nb_requests += 1
            except Exception:
                print(traceback.format_exc())
                break
            if result.status_code == 200:
                return result
            print(result.status_code)
            # Ajout du log de l'erreur ?
            nb_requests += 1

    def absolute_links(self, soup):
        for a in soup.findAll('a'):
            if a.get('href'):
                href = a['href']
                absolute_url = urljoin(self.url, href)
                a['href'] = absolute_url
                print(absolute_url)
                if absolute_url not in self.links_with_text:
                    self.links_with_text.append(absolute_url)
        return self.links_with_text

    # Fonction qui renvoit True si l'url est déjà dans la collection cible, False sinon.
    def inserted_urls(self, link):
        for document in self.collection.find():
            if document["url_du_lien"] == link:
                print(f"{link} déja dans la base")
                return True
        return False

    def insert_links(self):
        # Requête HTTP sur la page cible
        r = self.url_request()
        # Parsing du code HTML de la page
        soup = bs4.BeautifulSoup(r.content, 'html.parser')
        decompte = 0
        for link in self.absolute_links(soup):
            if self.list_repositories is None:
                self.list_repositories = []
            if self.check_scope():
                if not self.inserted_urls(link):
                    self.collection.insert_one({"url_de_la_page": f"{r.url}", "url_du_lien": f"{link}"})
                    print(f"Bien inséré à la db :{link}")
                    decompte += 1
                    if decompte == self.limite:
                        break
