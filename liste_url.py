import requests
import bs4
from urllib.parse import urljoin, urlparse
import traceback


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
    print(f"{url} est hors du scope")
    return False


# Requête HTTP sur la page cible
def url_request(url):
    result = None
    nb_requests = 0
    while nb_requests < 10:
        try:
            result = requests.get(url)
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


# Fonction qui renvoit True si l'url est déjà dans la collection cible, False sinon.
def inserted_urls(url, collection):
    for document in collection.find():
        if document["url_du_lien"] == url:
            print(f"{url} déja dans la base")
            return True
    return False


def insert_links(url, collection, list_domains, list_repositories=None, limite=None):
    # Requête HTTP sur la page cible
    r = url_request(url)
    # Parsing du code HTML de la page
    soup = bs4.BeautifulSoup(r.content, 'html.parser')
    decompte = 0
    for link in absolute_links(r.url, soup):
        if list_repositories is None:
            list_repositories = []
        if check_scope(link, list_domains, list_repositories):
            if not inserted_urls(link, collection):
                collection.insert_one({"url_de_la_page": f"{r.url}", "url_du_lien": f"{link}"})
                print(f"Bien inséré à la db :{link}")
                decompte += 1
                if decompte == limite:
                    break
