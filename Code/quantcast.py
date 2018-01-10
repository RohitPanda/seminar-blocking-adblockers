import urllib.request
from bs4 import BeautifulSoup

list_sites = []
num = 200 #upto 200

for i in range(1, num):
    url = 'https://www.quantcast.com/top-sites/DE/' + str(i)
    with urllib.request.urlopen(url) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        pretty_html = soup.prettify()
        with open(str(i) + '.hmtl', 'w') as f:
            f.write(pretty_html)
        all_td = soup.find_all("td", class_="link")
        for td in all_td:
            site = td.find('a')
            if site:
                #print(site.string)
                list_sites.append(site.string)

print(len(list_sites))

with open('top_sites_DE.txt', 'w') as f:
    for site in list_sites:
        f.write(site + '\n')
