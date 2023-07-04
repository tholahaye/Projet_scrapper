import requests
import bs4
from urllib.parse import urljoin, urlparse
import traceback


class ScrappingSession:
    def __init__(self, url, collection, list_domains, list_directories=None, limite=None):
        self.url = url
        self.collection = collection
        self.list_domains = list_domains
        self.list_directories = list_directories
        self.limite = limite
        self.links_with_text = []

    def check_domain(self, link):
        parsed_url = urlparse(link)
        for domain in self.list_domains:
            if parsed_url.netloc.endswith(domain):
                return True
        return False

    def check_directory(self, link):
        parsed_url = urlparse(link)
        for directory in self.list_directories:
            if parsed_url.path.startswith(directory):
                return True
        return False

    def check_scope(self, link):
        if self.check_domain(link):
            if len(self.list_directories) == 0:
                return True
            if self.check_directory(link):
                return True
        print(f"{link} est hors du scope")
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

    def textscrap(self, soup):
        h1 = []
        h2 = []
        titre = []
        important = []
        for text in soup.findAll('title'):
            titre.append(text.text)
        for text in soup.findAll('h1'):
            h1.append(text.text)
        for text in soup.findAll('h2'):
            h2.append(text.text)
        for text in soup.findAll(['b', 'strong', 'em']):
            important.append(text.text)

        print("titre")
        print(titre)
        print("h1")
        print(h1)
        print("h2")
        print(h2)
        print("élément b / stong / em")
        print(important)

        return {"titre": titre, "h1": h1, "h2": h2, "élément en gras": important}

    def insert_links(self):
        # Requête HTTP sur la page cible
        r = self.url_request()
        # Parsing du code HTML de la page
        soup = bs4.BeautifulSoup(r.content, 'html.parser')
        decompte = 0
        for link in self.absolute_links(soup):
            if self.list_directories is None:
                self.list_directories = []
            if self.check_scope(link):
                if not self.inserted_urls(link):
                    self.collection.insert_one({"url_de_la_page": f"{r.url}", "url_du_lien": f"{link}"})
                    print(f"Bien inséré à la db :{link}")
                    decompte += 1
                    if decompte == self.limite:
                        break
