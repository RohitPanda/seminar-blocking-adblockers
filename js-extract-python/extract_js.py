from __future__ import division
import hashlib
import json
import haralyzer
import utils
import logging
import glob
from BeautifulSoup import BeautifulSoup
import sys
import difflib
import progressbar
import os
import jsbeautifier

reload(sys)
sys.setdefaultencoding('utf8')

class ExtractJavascript:
    def __init__(self, params):
        self.params = params
        logging.debug("JS-Extractor. Parameters: %s" % utils.dict_to_string(self.params))
        self.embedded_stats, self.downloaded_stats, self.total_stats, self.script_clen, self.script_wlen = list(), list(), list(), list(), list()
        self.__extract_downloaded_js()
        self.__extract_embedded_js()
        json.dump(self.downloaded_stats, open(self.params["dst"] + "/download-stats.log","w"))
        json.dump(self.embedded_stats, open(self.params["dst"] + "/embedded-stats.log","w"))
        json.dump(self.total_stats, open(self.params["dst"] + "/all-stats.log", "w"))
        l = open(self.params["dst"] + "/extracted-script-stats", "w")
        self.script_clen.sort()
        self.script_wlen.sort()
        # print self.script_lengths
        for i in range(0, min(len(self.script_wlen), self.script_clen)):
            l.write(str(i/min(len(self.script_wlen), len(self.script_clen))) + "\t" + str(self.script_clen[i]) + "\t" + str(self.script_wlen[i]) + "\n")
        l.close()

    def __extract_embedded_js(self):
        logging.info("Extracting non-empty embedded JS from HTML sources")
        if self.params["html"] is None:
            self.embedded_stats = []
            return
        hashes = list()
        html_files = glob.glob(self.params["html"] + "/*.html")
        bar = progressbar.ProgressBar(maxval=len(html_files), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        #bar.start()
        count = 0
        for html_file in html_files:
            count += 1
	    #bar.update(count) 
            domain_list = list()
            site_index = html_file.split("/")[-1].split(".")[0]
            with open(html_file) as f:
                html_code = ''.join(f.readlines())
            try:
                valid_scripts = list()
                total_scripts, script_index, soup = 1, 1, BeautifulSoup(html_code)
                for tag in soup.findAll('script'):
                    ignore_script = False
                    if tag.text is None:
                        continue
                    if "src" not in tag.attrs and len(tag.text) == 0:
                        continue
                    if len(tag.text) == 0:
                        continue
                    if len(str(tag.text).replace(" ", "")) < self.params["minchars"]:
                        continue
                    if len(str(tag.text).replace(" ", "")) > self.params["maxchars"]:
                        continue
                    total_scripts += 1
                    for script in valid_scripts:
                        s = difflib.SequenceMatcher(None, script, str(tag.text).replace(" ", ""))
                        if s.quick_ratio() > self.params["sim"]:
                            ignore_script = True
                            break
                    if ignore_script:
                        logging.debug("Already found an almost identical JS from the same site. Ignoring this one.")
                        continue
                    hash_object = hashlib.sha512(bytes(str(tag.text)))
                    hex_dig = hash_object.hexdigest()
                    if hex_dig in hashes:
                        logging.debug("Already found an identical JS from the same site. Ignoring this one.")
                        continue
                    hashes.append(hex_dig)
                    beautified = jsbeautifier.beautify(str(tag.text))
                    wcount = len(beautified.split())
                    valid_scripts.append(str(tag.text).replace(" ", ""))
                    self.script_clen.append(len(str(tag.text).replace(" ", "")))
                    self.script_wlen.append(wcount)
                    foldername = os.getcwd() + "/" + self.params["dst"] + "/embedded-" + site_index + "-" + str(script_index) + "/"
                    logging.debug("Creating folder: %s" % foldername)
                    utils.make_folder(foldername)
                    filename = foldername + "embedded-" + str(site_index) + "-" + str(script_index) + ".js"
                    o = open(filename, "w")
                    domains = utils.find_domains_in_string(str(tag))
                    domain_list += domains
                    self.total_stats.append({"site": site_index, "script-id": script_index, "domains": list(set(domains)), "type": "embedded", "len": len(str(tag).replace(" ","")), "request-url": None, "path": filename, "wcount": wcount})
                    script_index += 1
                    o.write(beautified)
                    o.close()
                logging.info("Found %d scripts in file: %s (%d scripts including duplicates)" % (script_index, html_file, total_scripts))
                stats = {"index": site_index, "script-count": script_index, "domains": list(set(domain_list)), "type": "embedded"}
                self.embedded_stats.append(stats)
            except Exception as ex:
                logging.debug("Exception %s occurred while extracting scripts from file: %s" % (ex, html_file))

    def __extract_downloaded_js(self):
        logging.info("Extracting non-empty downloaded JS from HAR sources")
        if self.params["har"] is None:
            self.downloaded_stats = []
            return
        har_map = self.__match_har_with_url()
        bar = progressbar.ProgressBar(maxval=len(har_map.keys()), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        #bar.start()
        count = 0
        for key in har_map.keys():
            count += 1
            #bar.update(count)
            domain_list = list()
            hashes = list()
            valid_scripts = list()
            script_index, total_scripts = 1, 1
            for har_file in har_map[key]:
                with open(har_file) as hf:
                    har_parser = haralyzer.HarParser(json.loads(hf.read()))
                for page in har_parser.pages:
                    for js_file_ in page.js_files:
                        try:
                            js_file = js_file_["response"]["content"]["text"]
                            try:
                                js_url = js_file_["request"]["url"]
                            except Exception as ex:
                                logging.debug("Exception %s encountered while getting request URL" % ex)
                            if js_file is None:
                                continue
                            if js_url is None:
                                continue
                            if len(str(js_file).replace(" ", "")) < self.params["minchars"]:
                                continue
                            if len(str(js_file).replace(" ", "")) > self.params["maxchars"]:
                                continue
                            ignore_script = False
                            total_scripts += 1
                            for script in valid_scripts:
                                s = difflib.SequenceMatcher(None, script, str(js_file))
                                if s.quick_ratio() > self.params["sim"]:
                                    ignore_script = True
                                    break
                            if ignore_script:
                                logging.debug("Already found an almost identical JS from the same site. Ignoring this one.")
                                continue
                            hash_object = hashlib.sha512(bytes(str(js_file)))
                            hex_dig = hash_object.hexdigest()
                            if hex_dig in hashes:
                                logging.debug("Already found an identical JS from the same site. Ignoring this one.")
                                continue
                            hashes.append(hex_dig)
                            beautified = jsbeautifier.beautify(str(js_file))
                            wcount = len(beautified.split())
                            valid_scripts.append(str(js_file).replace(" ", ""))
                            self.script_clen.append(len(str(js_file).replace(" ", "")))
                            self.script_wlen.append(wcount)
                            foldername = os.getcwd() + "/" + self.params["dst"] + "/downloaded-" + key + "-" + str(script_index) + "/"
                            logging.debug("Creating folder: %s" % foldername)
                            utils.make_folder(foldername)
                            filename = foldername + "/downloaded-" + key + "-" + str(script_index) + ".js"
                            o = open(filename, "w")
                            domains = utils.find_domains_in_string(str(js_file))
                            self.total_stats.append({"site": key, "url": self.params["url-map"][str(key)],
                                                     "script-id": script_index, "domains": list(set(domains)),
                                                     "type": "downloaded", "len": len(str(js_file)),
                                                     "request-url": js_url, "path": filename, "wcount": wcount})
                            script_index += 1
                            domain_list += domains
                            o.write(str(beautified))
                            o.close()
                        except Exception as ex:
                            logging.debug("Encountered %s exception while parsing HAR file for JS" % ex)
            logging.info("Found %d scripts for url-index : %s (%d scripts including duplicates)" % (script_index, key, total_scripts))
            stats = {"index": key, "url": self.params["url-map"][key], "script-count": script_index, "domains": list(set(domain_list)), "type": "downloaded"}
            self.downloaded_stats.append(stats)

    def __match_har_with_url(self):
        har_files = sorted(glob.glob(self.params["har"] + "/*.har"), key=os.path.getmtime, reverse=True)
        found_count = 0
        har_file_map = dict()
        for har_file in har_files:
            domain_har = har_file.split("/")[-1].split(".har")[0]
            logging.debug("Domain of HAR file: %s -> %s" % (har_file, domain_har))
            try:
                for index in range(0, len(self.params["url-map"])):
                    if self.params["url-map"][str(index)] == domain_har:
                        logging.debug("Found a matching url %s for HAR domain: %s" % (self.params["url-map"][str(index)], domain_har))
                        found_count += 1
                        try:
                            har_file_map[str(index)].append(har_file)
                            # if len(har_file_map[str(index)]) > 0:
                            #     break
                        except Exception:
                            har_file_map[str(index)] = list()
                            har_file_map[str(index)].append(har_file)
                        continue
                    www_striped_domain_har = domain_har.lstrip("www.")
                    if self.params["url-map"][str(index)] == www_striped_domain_har:
                        logging.debug("Found a matching url %s for HAR domain (stripped): %s" % (self.params["url-map"][str(index)], www_striped_domain_har))
                        found_count += 1
                        try:
                            if len(har_file_map[str(index)]) > 0:
                                break
                        except Exception:
                            har_file_map[str(index)] = list()
                            har_file_map[str(index)].append(har_file)
            except Exception as ex:
                logging.debug("Exception %s occurred while matching HAR files with URLs" % ex)
        return har_file_map
