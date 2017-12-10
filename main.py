import sys
import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup as bs4


MAIL_REGEX = re.compile(r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+', re.MULTILINE | re.IGNORECASE)

def normalize_url(url, current_page=None):
    '''Function for normalization of the received URL.
    
    Allows the query to be executed if the URL contains
    only the domain name, relative address or missing schema.
    
    '''
    url = url.strip()
    url = url[:url.index('#')] if '#' in url else url
    if url.startswith('//'):
        url = 'http:' + url
    elif not (url.startswith('http://') or url.startswith('https://')) \
            and not url.startswith('/'):
        url = 'http://' + url
    elif current_page:
        url = urljoin(current_page, url)
    return url

def get_params():
    '''The function takes the RLC and the scan depth.
    
    The first parameter is the address. 
    Second, scan depth, default 1.
    '''

    depth = 1
    if sys.argv[1:2]:
        del sys.argv[0:1]
        url = sys.argv.pop(0)
        if sys.argv:
            try:
                depth = int(sys.argv.pop(0))
            except ValueError:
                print('Incorrect depth. Default 1')
    else:
        url = input('Enter URL: ')
        try:
            depth = int(input('Enter depth: '))
        except ValueError:
            print('Incorrect depth. Default 1')
    return url, depth

def get_crawl(url, depth):
    '''Function of making requests and receiving data.
    
    It takes the URL as a parameter and the depth of the scan.
    On the first iteration, it extracts addresses and URLs for
    further scanning, in the second iteration retrieves addresses
    from all the received URLs from the first iteration.
    Returns the set of e-mail addresses.
    
    '''
    all_mails = set()
    crawled_urls = set()
    uncrawled_urls = set()
    uncrawled_urls.add(url)
    depth = depth
    
    def get_data(page):
        
        mails = set(re.findall(MAIL_REGEX, page.text))
        print(mails.difference(all_mails))
        all_mails.update(mails)
    
        soup = bs4(page.text, 'lxml')
        links = soup.findAll('a', href=True)
        for link in links:
            if 'tel:' in link['href']:
                continue
            else:
                url = normalize_url(link['href'], page.url)
                uncrawled_urls.add(url)
    
    def get_page(*args):
        
        for url in args:
            if url in crawled_urls:
                continue
            else:
                try:
                    page = requests.get(url)
                except requests.RequestException:
                    print('Houston, we have a problem with', url)
                crawled_urls.add(url)
                get_data(page)
            
    for _ in range(depth):
        
        layer = len(uncrawled_urls) 
        for _ in range(layer):
            get_page(*uncrawled_urls)
    
    return all_mails
        

def main():
    '''The main function of the program, the entry point.
    
    Calls a function to get parameters and determines the
    further operation of the program.
    
    '''
    url, depth = get_params()
    url = normalize_url(url) 
    mails = get_crawl(url, depth)
    
    print('\n\nAll emails:\n')
    for i in mails:
        print(i)

if __name__ == "__main__":
    main()
