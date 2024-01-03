from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import urllib.request
import time
def main():
    TAG_URL = 'https://www.bookbrowse.com/reviews/index.cfm/book_number/2428'
    response = urllib.request.urlopen(TAG_URL)
    soup = BeautifulSoup(response, 'lxml')
    alikes = soup.find('div', class_='readalikes_content clear').find_all('li')
    for alike in alikes:
        bbid = alike.figure.a['href'].split('/')[-2]
        #Hacer lo que falte
    tags = soup.find('div', id='genres_themes').find_all('li')
    for tag in tags:
        name = tag.a.text.strip()
        print(name)
    

if __name__ == '__main__':
    main()