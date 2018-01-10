#Usage : seminar.py > Log-<Date>.txt

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from os import mkdir, makedirs
import re
import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer
import csv

stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]
    

current_dir = '/home/rohit/chromedriver'
chromedriver_path = '/usr/bin/chromedriver'

url_path = '/home/rohit/chromedriver/url-list.txt'

csv_path = '/home/rohit/chromedriver/features.csv'

#Changes can be made in the Adblock configuration to this Profile
profile_path = '/home/rohit/.config/google-chrome/Profile 1/'

sleep_time = 3

f = open(url_path, 'r')
sites = f.readlines()

csvfile = open(csv_path, 'w', newline='')
writer = csv.writer(csvfile)

writer.writerow(['site', 'lines', 'words', 'tags', 'div', 'h1', 'h2', 'h3', 'img', 'table', 'p', 'a', 'iframe', 'keyword', 'url_change', 'cosine_similarity', 'Anti-Adblock'])

for site in sites:
    
    site = site.rstrip()
    
    output_dir = current_dir + '/' + site
    print(output_dir)
    makedirs(output_dir, exist_ok=True)
    
    chrome_options = Options()
    chrome_options.add_argument("start-maximized");
    
    chrome_options.add_argument("user-data-dir="+profile_path);    
    driver = webdriver.Chrome(chromedriver_path, chrome_options=chrome_options)
    
    url = "http://www."+site
    print(url)
    
    driver.get(url)
    time.sleep(sleep_time)
    
    url_redirect_adb = driver.current_url
    print(url_redirect_adb)
    
    driver.save_screenshot(output_dir + '/' + 'adblock.png')
    content = driver.page_source
    
    driver.quit()
    
    soup = BeautifulSoup(content, 'html.parser')
    html_adblock = soup.prettify()
    with open(output_dir + '/' + 'adblock.html', "w") as file:
        file.write(html_adblock)
    
    all_text_adb = [text for text in soup.stripped_strings]
    no_words_adb = 0
    for text in all_text_adb:
      no_words_adb = no_words_adb + len(text.split())
    all_tags_adb = len(soup.find_all())
    all_divs_adb = len(soup.find_all('div'))
    all_h1_adb = len(soup.find_all('h1'))
    all_h2_adb = len(soup.find_all('h2'))
    all_h3_adb = len(soup.find_all('h3'))
    all_img_adb = len(soup.find_all('img'))
    all_table_adb = len(soup.find_all('tr'))
    all_p_adb = len(soup.find_all('p'))
    all_anchor_adb = len(soup.find_all('a'))
    all_iframe_adb = len(soup.find_all('iframe'))
    
    print(len(all_text_adb))
    print(no_words_adb)
    print(all_tags_adb)
    print(all_divs_adb)
    print(all_h1_adb)
    print(all_h2_adb)
    print(all_h3_adb)
    print(all_img_adb)
    print(all_table_adb)
    print(all_p_adb)
    print(all_anchor_adb)
    print(all_iframe_adb)
    print(len(soup(text=re.compile('adblocker|adblock|ad block|ad-block|whitelist|block-adblock|pagefair|fuckadblock', re.I))))
    
    keyword_present = 0
    if (len(soup(text=re.compile('adblocker|adblock|ad block|ad-block|whitelist|block-adblock|pagefair|fuckadblock', re.I)))) > 0:
        keyword_present = 1
    
    
    chrome_options = Options()
    chrome_options.add_argument("start-maximized");
    
    driver = webdriver.Chrome(chromedriver_path, chrome_options=chrome_options)
    
    
    driver.get(url)
    
    time.sleep(sleep_time)
    
    url_redirect= driver.current_url
    print(url_redirect)
    
    driver.save_screenshot(output_dir + '/' + 'noadblock.png')
    content = driver.page_source
    
    driver.quit()
    
    soup = BeautifulSoup(content, 'html.parser')
    html_noadblock = soup.prettify()
    with open(output_dir + '/' + 'noadblock.html', "w") as file:
        file.write(html_noadblock)
    
    all_text = [text for text in soup.stripped_strings]
    no_words = 0
    for text in all_text:
      no_words = no_words + len(text.split())
    all_tags = len(soup.find_all())
    all_divs = len(soup.find_all('div'))
    all_h1 = len(soup.find_all('h1'))
    all_h2 = len(soup.find_all('h2'))
    all_h3 = len(soup.find_all('h3'))
    all_img = len(soup.find_all('img'))
    all_table = len(soup.find_all('tr'))
    all_p = len(soup.find_all('p'))
    all_anchor = len(soup.find_all('a'))
    all_iframe = len(soup.find_all('iframe'))
    
    print(len(all_text))
    print(no_words)
    print(all_tags)
    print(all_divs)
    print(all_h1)
    print(all_h2)
    print(all_h3)
    print(all_img)
    print(all_table)
    print(all_p)
    print(all_anchor)
    print(all_iframe)
    print (len(soup(text=re.compile('adblocker|adblock|ad block|ad-block|whitelist|block-adblock|pagefair|fuckadblock', re.I))))
    
    if url_redirect_adb == url_redirect:
        url_change = 0
    else:
        url_change = 1
    print(url_change)
    
    #site, lines, words, tags, div, h1, h2, h3, img, table, p, a, iframe, keyword, url_change, cosine_similarity
    feature_list = []
    feature_list.append(site)
    feature_list.append(len(all_text) - len(all_text_adb))
    feature_list.append(no_words - no_words_adb)
    feature_list.append(all_tags - all_tags_adb)
    feature_list.append(all_divs - all_divs_adb)
    feature_list.append(all_h1 - all_h1_adb)
    feature_list.append(all_h2 - all_h2_adb)
    feature_list.append(all_h3 - all_h3_adb)
    feature_list.append(all_img - all_img_adb)
    feature_list.append(all_table - all_table_adb)
    feature_list.append(all_p - all_p_adb)
    feature_list.append(all_anchor - all_anchor_adb)
    feature_list.append(all_iframe - all_iframe_adb)
    feature_list.append(keyword_present)
    feature_list.append(url_change)
    feature_list.append(cosine_sim(html_noadblock, html_adblock))
    
    print(cosine_sim(html_noadblock, html_adblock))
    
    writer.writerow(feature_list)

f.close()
csvfile.close()

#Weka-Conversion
#java -cp /home/rohit/ML_SWT/weka-3-8-1/weka.jar weka.core.converters.CSVLoader features.csv -L "Anti-Adblock:TRUE,FALSE" > features.arff
