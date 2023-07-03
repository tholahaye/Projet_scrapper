import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

links_with_text = []

url = input("URL : ")
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

if response.status_code == 200:

else:
    print("error 404")
def absolute_links(url, soup):
    for a in soup.findAll('a'):
        if a.get('href'):
            href = a['href']
            if href.startswith('/'):
                absolute_url = urljoin(url, href)
                a['href'] = absolute_url
                links_with_text.append(absolute_url)


absolute_links(url, soup)

print("Liens avec du texte :")
print(links_with_text)