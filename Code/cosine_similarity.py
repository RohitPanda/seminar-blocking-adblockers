import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer
from bs4 import BeautifulSoup
import time
import csv
import os

start_time = time.time()

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
    
current_dir = '/home/rohit/chromedriver/Seminar/sites-1'

url_path = '/home/rohit/chromedriver/Seminar/sites-1/done'

csv_path = '/home/rohit/chromedriver/Seminar/sites-1/cosine-sim.csv'


f = open(url_path, 'r')
sites = f.readlines()

csvfile = open(csv_path, 'w', newline='')
writer = csv.writer(csvfile)

writer.writerow(['site', 'cosine_similarity'])

for site in sites:
    
    site = site.rstrip()
        
    output_dir = current_dir + '/' + site
    print(output_dir)

    if os.path.exists(output_dir) == False:
        continue
    
    with open(output_dir + '/' + 'adblock.html', "r") as file:
        html_adblock = file.readlines()
    
    with open(output_dir + '/' + 'noadblock.html', "r") as file:
        html_noadblock = file.readlines()
    
    similarity = cosine_sim(str(html_noadblock), str(html_adblock))
    
    feature_list = []
    feature_list.append(site)
    feature_list.append(similarity)
    
    print(similarity)
    
    writer.writerow(feature_list)

f.close()
csvfile.close()


print('\nTook ' + str(time.time() - start_time) + 's\n')
