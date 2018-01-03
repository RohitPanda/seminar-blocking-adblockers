import os
import logging
import re
import json


def make_folder(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError as ex:
        logging.debug("Exception %s occurred while creating folder : %s " % (ex, path))


def load_url_index_dict(path):
    d = dict()
    try:
        f = open(path)
        for line in f:
            index, url = line.split(",")[0].strip(), line.split(",")[1].strip()
            d[str(int(index)-1)] = url
            logging.debug("Adding Index: %s -> URL: %s entry" % (index, url))
    except Exception as ex:
        logging.debug("Exception %s occurred while creating index-url dict mapping" % ex)
    return d


def dict_to_string(dictionary):
    string = None
    try:
        string = ' | '.join('({}) {}'.format(key, val) for key, val in sorted(dictionary.items()))
    except AttributeError as ex:
        logging.debug("Exception (%s) while converting dictionary to string." % ex)
    return string


def dict_to_file(d, f):
    json.dump(d, open(f, "w"))


def file_to_dict(f):
    d = json.load(open(f))
    return d




def to_json(list):
    return json.dumps(list)


def find_domains_in_string(string):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    domains = list()
    for url in urls:
        domain = url.split("/")[2]
        if domain.count(".") == 2:
            if domain.split(".")[2].isalnum():
                domains.append(domain)
                logging.debug("Found domain: %s" % domain)
    return set(domains)
