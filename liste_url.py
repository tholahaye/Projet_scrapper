import requests
import bs4
from urllib.parse import urljoin, urlparse


def check_domain(url, list_domains):
    parsed_url = urlparse(url)
    for domain in list_domains:
        if parsed_url.netloc.endswith(domain):
            return True
    return False


def check_repository(url, list_repository):
    parsed_url = urlparse(url)
    for repository in list_repository:
        if parsed_url.path.startswith(repository):
            return True
    return False


def check_scope(url, list_domains, list_repositories):
    if check_domain(url, list_domains):
        if len(list_repositories) == 0:
            return True
        if check_repository(url, list_repositories):
            return True
    return False


def absolute_links(url, soup):
    links_with_text = []
    for a in soup.findAll('a'):
        if a.get('href'):
            href = a['href']
            absolute_url = urljoin(url, href)
            a['href'] = absolute_url
            links_with_text.append(absolute_url)
    # Transformation en ensemble pour éliminer les doublons.
    links_with_text = set(links_with_text)
    return links_with_text


#Fonction qui renvoit True si l'url est déjà dans la collection cible, False sinon.
def inserted_urls(url, collection):
    for document in collection.find():
        if document["url_du_lien"] == url:
            return True
    return False


def insert_links(url, collection, list_domains, list_repositories=None, limite=None):
    r = requests.get(url) #Requête HTTP sur la page cible
    soup = bs4.BeautifulSoup(r.content, 'html.parser')#Parsing du code HTML de la page
    decompte = 0
    for link in absolute_links(r.url, soup):
        if list_repositories is None:
            list_repositories = []
        if check_scope(link, list_domains, list_repositories):
            if not inserted_urls(url, collection):
                collection.insert_one({"url_de_la_page": f"{r.url}", "url_du_lien": f"{link}"})
                print(f"Bien inséré à la db :{link}")
                decompte += 1
                if decompte == limite: #pour s'arrêter à la limite
                    break
