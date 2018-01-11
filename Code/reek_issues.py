import urllib.request
from bs4 import BeautifulSoup

list_sites = []
num = 58

for i in range(1, num):
    url = 'https://github.com/reek/anti-adblock-killer/issues?page=' + str(i) + '&q=is%3Aissue+is%3Aopen'
    with urllib.request.urlopen(url) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        #pretty_html = soup.prettify()
        #with open(str(i) + '.hmtl', 'w') as f:
        #    f.write(pretty_html)
        all_links = soup.find_all("a", class_="link-gray-dark no-underline h4 js-navigation-open")
        for link in all_links:
            site = link.string.rstrip().lstrip()
            if site:
                #print(site)
                list_sites.append(site)
print(len(list_sites))

with open('reek.txt', 'w') as f:
    for site in list_sites:
        f.write(site + '\n')
