from __future__ import division
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from javascript_stopwords import js_stopwords
from stop_words import get_stop_words
import numpy as np
import logging
import progressbar
import utils
import difflib
import json
import tld
import string


class SimilarityMethods:
    def __init__(self, file_map, params):
        self.file_map = file_map
        self.file_count = len(self.file_map)
        self.params = params
        self.file_stat_map = self._get_file_stat_map(self.file_map, json.load(open(self.params["stats"])))
        self.intersite = self.params["inter"]
        logging.info("Computing similarity scores between all pairs of (%d) input files" % self.file_count)
        self.worker_id = self.params["w-id"]
        self.total_workers = self.params["total-workers"]
        self.total_cells = .5 * (self.file_count * (self.file_count - 1))
        self.avg_work = self.total_cells/self.total_workers
        self.work_allocated = 0
        self.matrix = np.ones((self.file_count, self.file_count)) * -1
        self.cols_for_worker = list()
        self.__compute_cols_for_worker()
        if self.params["preload"] is None:
            self.__populate_matrix()
            self.__write_similarity_matrix()
        else:
            self.__load_similarity_matrix()
        self.tfidf = None
        self.__write_file_map()

    def _get_file_stat_map(self, filemap, stats):
        map_ = dict()
        logging.info("Performing mapping between files and stats")
        bar = progressbar.ProgressBar(maxval=len(filemap), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        for i in range(0, len(filemap)):
            try:
                bar.update(i)
                filename = filemap[i].split("/")[-1]
                site = filename.split("-")[1]
                script = filename.split("-")[2].split(".")[0]
                for s in stats:
                    if (str(s["script-id"]) == str(script)) and (str(s["site"]) == str(site)):
                        logging.debug("Found a match. Filename: %s | Script: %s (%s) | Site: %s (%s) " %
                                      (filename, script, str(s["script-id"]), site, str(s["site"])))
                        map_[i] = s
                        map_[i]["filename"] = filemap[i]
            except Exception as ex:
                logging.debug("Encountered an exception (%s) while mapping files with stats" % ex)
        return map_

    def difflib_quick_similarity_metric(self):
        logging.debug("Using the QuickDiffLib similarity metric to populate the matrix")
        current_comparisons = 0
        bar = progressbar.ProgressBar(maxval=self.work_allocated, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        for i in range(self.cols_for_worker[0], self.cols_for_worker[-1] + 1):
            try:
                f1_text = unicode(open(self.file_stat_map[i]["filename"]).read(), errors='ignore')
            except KeyError:
                continue
            f1_text = f1_text.replace(" ","")
            for j in range(0, i):
                logging.debug("Comparison: %d" % current_comparisons)
                current_comparisons += 1
                if self.matrix[i][j] != -1:
                    continue
                bar.update(current_comparisons)
                try:
                    f2_text = unicode(open(self.file_stat_map[j]["filename"]).read(), errors='ignore')
                except KeyError:
                    continue
                f2_text = f2_text.replace(" ","")
                s = difflib.SequenceMatcher(None, f1_text, f2_text)
                self.matrix[i][j] = s.quick_ratio()
                self.matrix[j][i] = self.matrix[i][j]
                logging.debug("File: %d (%s) and %d (%s) have a similarity score of: %f [QUICK-DIFFLIB]" %
                              (i, self.file_stat_map[i]["filename"], j, self.file_stat_map[j]["filename"],
                               self.matrix[i][j]))
        self.__write_similarity_matrix()

    def difflib_similarity_metric(self):
        logging.debug("Using the DiffLib similarity metric to populate the matrix")
        current_comparisons = 0
        bar = progressbar.ProgressBar(maxval=self.work_allocated, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        for i in range(self.cols_for_worker[0], self.cols_for_worker[-1] + 1):
            try:
                f1_text = unicode(open(self.file_stat_map[i]["filename"]).read(), errors='ignore')
            except KeyError:
                continue
            f1_text = f1_text.replace(" ","")
            for j in range(0, i):
                current_comparisons += 1
                logging.debug("Comparison: %d" % current_comparisons)
                if self.matrix[i][j] != -1:
                    continue
                bar.update(current_comparisons)
                try:
                    f2_text = unicode(open(self.file_stat_map[j]["filename"]).read(), errors='ignore')
                except KeyError:
                    continue
                f2_text = f2_text.replace(" ","")
                s = difflib.SequenceMatcher(None, f1_text, f2_text)
                self.matrix[i][j] = s.ratio()
                self.matrix[j][i] = self.matrix[i][j]
                logging.debug("File: %d (%s) and %d (%s) have a similarity score of: %f [DIFFLIB]" %
                              (i, self.file_stat_map[i]["filename"], j, self.file_stat_map[j]["filename"],
                               self.matrix[i][j]))
        self.__write_similarity_matrix()

    def tfidf_cosine_similarity_metric_fullcorpus(self):
        self.__generate_tfidf_corpus()
        # current_comparisons = 0
        # bar = progressbar.ProgressBar(maxval=self.work_allocated, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        # bar.start()
        # for i in range(self.cols_for_worker[0], self.cols_for_worker[-1] + 1):
        #     for j in range(0, i):
        #         current_comparisons += 1
                # if self.matrix[i][j] != -1:
                #     continue
                # bar.update(current_comparisons)
                # self.matrix[i][j] = self.tfidf.toarray()[i][j]
                # self.matrix[j][i] = self.matrix[i][j]
        self.matrix = self.tfidf.toarray()
        self.__write_similarity_matrix()

    def tfidf_cosine_similarity_metric_paircorpus(self):
        current_comparisons = 0
        bar = progressbar.ProgressBar(maxval=self.work_allocated, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
        for i in range(self.cols_for_worker[0], self.cols_for_worker[-1] + 1):
            try:
                f1_text = unicode(open(self.file_stat_map[i]["filename"]).read().translate(replace_punctuation), errors='ignore')
            except KeyError:
                continue
            for j in range(0, i):
                current_comparisons += 1
                logging.debug("Comparison: %d" % current_comparisons)
                if self.matrix[i][j] != -1:
                    continue
                bar.update(current_comparisons)
                try:
                    f2_text = unicode(open(self.file_stat_map[j]["filename"]).read().translate(replace_punctuation), errors='ignore')
                except KeyError:
                    continue
                try:
                    self.__generate_tfidf_pair(f1_text, f2_text)
                    self.matrix[i][j] = self.tfidf.toarray()[0][1]
                    self.matrix[j][i] = self.matrix[i][j]
                except ValueError:
                    self.matrix[i][j] = 0
                    self.matrix[j][i] = 0
        self.__write_similarity_matrix()

    def __generate_tfidf_corpus(self):
        data = list()
        logging.info("Computing TF-IDF for full corpus")
        replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
        for i in range(0, self.file_count):
            try:
                text = unicode(open(self.file_stat_map[i]["filename"]).read().translate(replace_punctuation), errors='ignore')
            except KeyError:
                continue
            #replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
            #text = text.translate(replace_punctuation)
            data.append(text)
        all_stop_words = js_stopwords + get_stop_words('english')
        tfidf = TfidfVectorizer(analyzer="word", stop_words=set(all_stop_words)).fit_transform(data)
        self.tfidf = tfidf * tfidf.T

    def __generate_tfidf_pair(self, text_1, text_2):
        # replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
        # text_1 = text_1.translate(replace_punctuation)
        # text_2 = text_2.translate(replace_punctuation)
        data = [text_1, text_2]
        all_stop_words = js_stopwords + get_stop_words('english')
        tfidf = TfidfVectorizer(analyzer="word", stop_words=set(all_stop_words)).fit_transform(data)
        self.tfidf = tfidf * tfidf.T

    def __compute_cols_for_worker(self):
        logging.info("Worker ID: %d (Total workers: %d). Expected work: %d cells (Total cells: %d)" %
                     (self.worker_id, self.total_workers, self.avg_work, self.total_cells))
        total_work_allocated = 0
        for worker in range(1, self.total_workers + 1):
            work_allocated_to_worker, running_sum = 0, 0
            for work in range(1, self.file_count):
                running_sum += work
                if (running_sum >= total_work_allocated) and (work_allocated_to_worker < self.avg_work):
                    work_allocated_to_worker += work
                    total_work_allocated += work
                    if worker == self.worker_id:
                        self.cols_for_worker.append(work)
                        self.work_allocated = work_allocated_to_worker
                elif work_allocated_to_worker >= self.avg_work:
                    break
        logging.info("Worker ID: %d | Start col: %d | End col: %d | Total work allocated: %d (%d)" %
                     (self.worker_id, self.cols_for_worker[0], self.cols_for_worker[-1], self.work_allocated,
                      total_work_allocated))

    def __populate_matrix(self):
        logging.info("Creating initial matrix")
        current_comparisons = 0
        filtered_count = {'intersite': 0, 'length': 0, 'words': 0, 'domains': 0, 'source': 0, 'blacklist': 0}
        b = open(self.params["blacklist"])
        blacklist = list()
        for line in b:
            blacklist.append(line.replace(" ","").strip())
        bar = progressbar.ProgressBar(maxval=self.work_allocated, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        for i in range(self.cols_for_worker[0], self.cols_for_worker[-1] + 1):
            self.matrix[i][i] = 0
            for j in range(0, i):
                current_comparisons += 1
                bar.update(current_comparisons)
                # Length, word, domain, and request URL filter
                try:
                    # Inter-site filter
                    if self.intersite and (self.file_stat_map[i]["site"] == self.file_stat_map[j]["site"]):
                        logging.debug("Inter-site only flag is on and we have %s (%s) being compared with %s (%s). "
                                      "Setting similarity to 0." % (self.file_stat_map[i]["filename"],
                                                                    self.file_stat_map[i]["site"],
                                                                    self.file_stat_map[j]["filename"],
                                                                    self.file_stat_map[j]["site"]))
                        self.matrix[i][j] = 0
                        self.matrix[j][i] = 0
                        filtered_count['intersite'] += 1
                        continue
                    # Length filter
                    if min(int(self.file_stat_map[i]["len"]), int(self.file_stat_map[j]["len"]))/max(int(self.file_stat_map[i]["len"]), int(self.file_stat_map[j]["len"])) < float(self.params["ratio"]):
                        logging.debug("Pair: %s and %s. Filtered by length filter" %
                                      (self.file_stat_map[i]["filename"], self.file_stat_map[j]["filename"]))
                        self.matrix[i][j] = 0
                        self.matrix[j][i] = 0
                        filtered_count['length'] += 1
                        continue
                    # Word count filter
                    if min(int(self.file_stat_map[i]["wcount"]), int(self.file_stat_map[j]["wcount"]))/max(int(self.file_stat_map[i]["wcount"]), int(self.file_stat_map[j]["wcount"])) < float(self.params["ratio"]):
                        logging.debug("Pair: %s and %s. Filtered by word filter" %
                                      (self.file_stat_map[i]["filename"], self.file_stat_map[j]["filename"]))
                        self.matrix[i][j] = 0
                        self.matrix[j][i] = 0
                        filtered_count['words'] += 1
                        continue
                    # Domain filter
                    if (len(self.file_stat_map[i]["domains"]) == 0) and (len(self.file_stat_map[j]["domains"]) > 0):
                        logging.debug("Pair: %s and %s. Filtered by domain filter" %
                                      (self.file_stat_map[i]["filename"], self.file_stat_map[j]["filename"]))
                        self.matrix[i][j] = 0
                        self.matrix[j][i] = 0
                        filtered_count['domains'] += 1
                        continue
                    if (len(self.file_stat_map[i]["domains"]) > 0) and (len(self.file_stat_map[j]["domains"]) == 0):
                        logging.debug("Pair: %s and %s. Filtered by domain filter" %
                                      (self.file_stat_map[i]["filename"], self.file_stat_map[j]["filename"]))
                        self.matrix[i][j] = 0
                        self.matrix[j][i] = 0
                        filtered_count['domains'] += 1
                        continue
                    # Dont check the blacklist or source if this is an embedded script
                    if self.file_stat_map[i]["type"] == "embedded":
                        continue
                    if self.file_stat_map[j]["type"] == "embedded":
                        continue
                    # Source filter
                    if self.file_stat_map[i]["request-url"] == self.file_stat_map[j]["request-url"]:
                        if(self.file_stat_map[i]["request-url"] is None) or (self.file_stat_map[j]["request-url"] is None):
                            continue
                        if(self.file_stat_map[i]["request-url"] == "null") or (self.file_stat_map[j]["request-url"] == "null"):
                            continue
                        logging.debug("Pair: %s and %s. Filtered by source filter" %
                                      (self.file_stat_map[i]["filename"], self.file_stat_map[j]["filename"]))
                        self.matrix[i][j] = 1
                        self.matrix[j][i] = 1
                        filtered_count['source'] += 1
                        continue
                    # Blacklist filter
                    found_entry = 0
                    for entry in blacklist:
                        # print entry, str(self.file_stat_map[i]["request-url"]).replace(" ", "").strip()
                        try:
                            if entry == tld.get_tld(str(self.file_stat_map[i]["request-url"]).replace(" ","").strip(), as_object=True).domain:
                                logging.debug("Pair: %s and %s. Filtered by blacklist filter" %
                                              (self.file_stat_map[i]["filename"], self.file_stat_map[j]["filename"]))
                                # print entry, self.file_stat_map[i]["request-url"]
                                found_entry = 1
                                break
                        except Exception as ex:
                            continue 
                    if found_entry == 1:
                        self.matrix[i][j] = 0
                        self.matrix[j][i] = 0
                        filtered_count['blacklist'] += 1
                        continue
                    for entry in blacklist:
                        # print entry, str(self.file_stat_map[i]["request-url"]).replace(" ", "").strip()
                        try:
                            if entry == tld.get_tld(str(self.file_stat_map[j]["request-url"]).replace(" ","").strip(), as_object=True).domain:
                                logging.debug("Pair: %s and %s. Filtered by blacklist filter" %
                                              (self.file_stat_map[i]["filename"], self.file_stat_map[j]["filename"]))
                                # print entry, self.file_stat_map[i]["request-url"]
                                found_entry = 1
                                break
                        except Exception as ex:
                            continue
                    if found_entry == 1:
                        self.matrix[i][j] = 0
                        self.matrix[j][i] = 0
                        filtered_count['blacklist'] += 1
                        continue
                except (ZeroDivisionError, KeyError):
                    self.matrix[i][j] = 0
                    self.matrix[j][i] = 0
                    continue
        bar.finish()
        logging.info("Filter Stats| Total comparisons: %d, Intersite: %d, Length: %d, Words: %d, Domains: %d, "
                     "Source: %d, Blacklist: %d" % (current_comparisons, filtered_count['intersite'],
                                                    filtered_count['length'], filtered_count['words'],
                                                    filtered_count['domains'], filtered_count['source'],
                                                    filtered_count['blacklist']))

    def __write_similarity_matrix(self):
        np.save(file=self.params["output"]+"/similarity-matrix-"+str(self.worker_id), arr=self.matrix)

    def __write_file_map(self):
        fullmap = dict()
        stats = utils.file_to_dict(self.params["stats"])
        for key in self.file_map.keys():
            path = self.file_map[key]
            filename = self.file_map[key].split("/")[-1]
            try:
                type_ = filename.split("-")[0]
                site_ = filename.split("-")[1]
                script_ = filename.split("-")[2].split(".")[0]
                for entry in stats:
                    if (entry["script-id"] == int(script_)) and (entry["type"] == type_) and (entry["site"] == site_):
                        record = {"file": path, "script-id": script_, "type": type_, "site": site_, "url": entry["url"],
                                  "domains": entry["domains"], "id": key, "source": entry["request-url"]}
                        fullmap[key] = record
            except Exception as ex:
                logging.info("Encountered exception %s while parsing filemap" % ex)
        utils.dict_to_file(fullmap, self.params["output"]+"/filemap")


    def __load_similarity_matrix(self):
        self.matrix = np.load(self.params["preload"])
        logging.info("Loaded a %s matrix" % str(self.matrix.shape))
