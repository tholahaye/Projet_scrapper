import requests
import bs4
from urllib.parse import urljoin


def absolute_links(url, soup):
    links_with_text = []
    for a in soup.findAll('a'):
        if a.get('href'):
            href = a['href']
            if href.startswith('/'):
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


def insert_links(url, collection, limite=None):
    r = requests.get(url) #Requête HTTP sur la page cible
    soup = bs4.BeautifulSoup(r.content, 'html.parser')#Parsing du code HTML de la page
    decompte = 0
    for link in absolute_links(r.url, soup):
        if not inserted_urls(url, collection):
            collection.insert_one({"url_de_la_page": f"{r.url}", "url_du_lien": f"{link}"})
            print(f"Bien inséré à la db :{link}")
            decompte += 1
            if decompte == limite: #pour s'arrêter à la limite
                break