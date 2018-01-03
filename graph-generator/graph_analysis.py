from __future__ import division, unicode_literals
from sklearn.feature_extraction.text import TfidfVectorizer
from javascript_stopwords import js_stopwords
from stop_words import get_stop_words
import html
import random
import string
import logging
import numpy as np
import networkx as nx
import utils
import glob
import matplotlib.pyplot as plt
import progressbar
import collections
import operator

class GraphAnalysis:
    def __init__(self, params):
        self.params = params
        self.input_folder = params["input"]
        self.output_folder = params["output"]
        self.threshold = float(params["threshold"])
        self.filemap = utils.file_to_dict(params["filemap"])
        self.adjacency_matrix = -1 * np.ones((len(self.filemap.keys()), len(self.filemap.keys())))
        self.__load_matrix()
        self.graph = None
        self.__generate_graph()
        self.cliques = dict()
        if self.params["cliques"]:
            features_dict = self.__build_feature_dictionary()
            self.__get_maximal_cliques(features_dict)
            iterations = 0
            while iterations < 1:
                iterations += 1
                self.__make_nonzero_cliques()
                self.__generate_graph()
                self.__get_maximal_cliques(features_dict)
            self.__compute_clique_stats()
            self.__create_html_results()

    def __load_matrix(self):
        logging.info("Merging matrices to create a single adjacency matrix")
        npy_files = glob.glob(self.input_folder + "/*.npy")
        bar = progressbar.ProgressBar(maxval=len(self.filemap.keys())*len(self.filemap.keys()), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        counter = 0
        list_of_matrices = list()
        for file in npy_files:
            matrix = np.load(file)
            list_of_matrices.append(matrix)
        for i in range(0, len(self.filemap.keys())):
            self.adjacency_matrix[i][i] = 1
            for j in range(0, len(self.filemap.keys())):
                counter += 1
                bar.update(counter)
                l = list()
                for k in range(0, len(list_of_matrices)):
                    l.append(list_of_matrices[k][i][j])
                self.adjacency_matrix[i][j] = max(max(l), 0)
        logging.info("Loaded a %s matrix" % str(self.adjacency_matrix.shape))

    def __generate_graph(self):
        logging.info("Generating graph from adjacency matrix")
        self.graph = nx.Graph()
        bar = progressbar.ProgressBar(maxval=len(self.filemap.keys()), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        for i in range(0, len(self.filemap.keys())):
            try:
                bar.update(i)
                boolean_threshold_array = self.adjacency_matrix[i]
                if (boolean_threshold_array>self.threshold)[0:].sum() < self.params["clique-size"]:
                    logging.debug("Not adding node %d to graph. It has no chance of being in a clique we care about" % i)
                    # print (boolean_threshold_array>self.threshold)[0:], (boolean_threshold_array>self.threshold)[0].sum()
                    continue
                self.graph.add_node(str(i))
                for j in range(0, i):
                    self.graph.add_node(str(j))
                    if self.adjacency_matrix[i][j] >= self.threshold:
                        self.graph.add_edge(i, j, {"JS-1": self.filemap[str(i)]["file"], "JS-2": self.filemap[str(j)]["file"], "threshold": self.adjacency_matrix[i][j]})
            except KeyError as ex:
                logging.debug("Exception %s encountered while constructing graph" % ex)
        if self.params["plot"]:
            pos = nx.spring_layout(self.graph)
            nx.draw(self.graph, pos, node_color='#A0CBE2', edge_color='#BB0000', width=.3, node_size=1)
            plt.savefig(self.output_folder+"/initial-graph.pdf", dpi=1000, facecolor='w', edgecolor='w',orientation='portrait', papertype=None, format=None,transparent=False, bbox_inches=None, pad_inches=0.1)

    def __build_feature_dictionary(self):
        corpus = list()
        logging.info("Building a feature dictionary")
        bar = progressbar.ProgressBar(maxval=len(self.filemap.keys()), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
        for i in range(0, len(self.filemap.keys())):
            try:
                bar.update(i)
                text = unicode(open(self.filemap[str(i)]["file"]).read().translate(replace_punctuation).lower(), errors='ignore')
                corpus.append(text)
            except Exception as ex:
                logging.debug("Exception %s encountered while loading corpus" % ex)
        vectorizer = TfidfVectorizer(analyzer="word", stop_words=js_stopwords)
        vectorizer.fit_transform(corpus)
        features = vectorizer.get_feature_names()
        features_dict = dict()
        for feature in features:
            features_dict[feature] = 1
        return features_dict

    def __get_maximal_cliques(self, features_dict):
        logging.info("Finding Maximal Cliques of size %d" % self.params["clique-size"])
        cliques = list(nx.find_cliques(self.graph))
        #features_dict = self.__build_feature_dictionary()
        self.cliques.clear()
        for clique_number, clique in enumerate(sorted([x for x in cliques if len(x) > self.params["clique-size"]], key=len, reverse=True)):
            logging.debug("Clique ID: %d | Clique Size: %d" % (clique_number, len(clique)))
            nodes = list()
            clique_string = ""
            for node in clique:
                try:
                    replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
                    n = self.filemap[str(node)]
                    text = unicode(open(n["file"]).read().translate(replace_punctuation), errors='ignore')
                    clique_string += text +"\t"
                except Exception as ex:
                    logging.debug("Exception %s encountered while loading clique documents" % ex)
                    continue
                node_dict = {"id": str(node), "site": n["site"], "script-id": n["script-id"], "url": n["url"], "file": n["file"], "source": n["source"], "domains": n["domains"]}
                nodes.append(node_dict)
            clique_strings = clique_string.split()
            logging.debug("Getting keywords from clique: %d which has a total of %d words" % (clique_number, len(clique_strings)))
            keywords = self.__get_keywords(clique_strings, features_dict)
            self.cliques[clique_number] = {"id": clique_number, "size": len(clique), "members": nodes, "keywords": keywords, "overlap": None, "n-1-similar-cliques": " "}
        logging.info("We have a total of %d cliques" % clique_number)

    def __make_nonzero_cliques(self):
        logging.info("Finding and possibly merging cliques with very similar members")
        bar = progressbar.ProgressBar(maxval=len(self.cliques.keys()) * len(self.cliques.keys()), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar_counter = 0
        bar.start()
        for key in self.cliques.keys():
            for s_key in self.cliques.keys():
                bar_counter += 1
                bar.update(bar_counter)
                if key == s_key:
                    continue
                clique_overlap = [i for i in self.cliques[key]["members"] for j in self.cliques[s_key]["members"] if i["id"] == j["id"]]
                if len(clique_overlap) >=  self.cliques[key]["size"] - 1:
                    for m1 in self.cliques[key]["members"]:
                        for m2 in self.cliques[s_key]["members"]:
                            if self.adjacency_matrix[int(m1["id"])][int(m2["id"])] == 0:
                                self.adjacency_matrix[int(m1["id"])][int(m2["id"])] = self.__compute_similarity(m1, m2)
                                self.adjacency_matrix[int(m2["id"])][int(m1["id"])] = self.adjacency_matrix[int(m1["id"])][int(m2["id"])]

    def __compute_similarity(self, node1, node2):
        replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
        try:
            f1_text = unicode(open(node1["file"]).read().translate(replace_punctuation), errors='ignore')
            f2_text = unicode(open(node2["file"]).read().translate(replace_punctuation), errors='ignore')
            data = [f1_text, f2_text]
        except KeyError:
            return 0
        all_stop_words = js_stopwords + get_stop_words('english')
        tfidf = TfidfVectorizer(analyzer="word", stop_words=set(all_stop_words)).fit_transform(data)
        sim = tfidf * tfidf.T
        return sim.toarray()[0][1]

    def __compute_clique_stats(self):
        logging.info("Computing Clique Statistics")
        bar = progressbar.ProgressBar(maxval=len(self.cliques.keys()) * len(self.cliques.keys()), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar_counter = 0
        bar.start()
        for key in self.cliques.keys():
            all_nodes = list()
            for s_key in self.cliques.keys():
                bar_counter += 1
                bar.update(bar_counter)
                if key == s_key:
                    continue
                for node in self.cliques[s_key]["members"]:
                    if node not in all_nodes:
                        all_nodes.append(node)
                clique_overlap = [i for i in self.cliques[key]["members"] for j in self.cliques[s_key]["members"] if i["id"]==j["id"]]
                if len(clique_overlap) >= self.cliques[key]["size"] - 1:
                    for m1 in self.cliques[key]["members"]:
                        for m2 in self.cliques[s_key]["members"]:
                            if (m1 not in clique_overlap) and (m2 not in clique_overlap) and (m1["id"] != m2["id"]):
                                score = str(max(self.adjacency_matrix[int(m1["id"])][int(m2["id"])], self.adjacency_matrix[int(m2["id"])][int(m1["id"])]))
                                self.cliques[key]["n-1-similar-cliques"] += " |C: " + str(self.cliques[s_key]["id"]) + " (" + str(m1["id"]) + "," + str(m2["id"]) +") " + ", S: " + str(score) + " | "
            self.cliques[key]["n-1-similar-cliques"] += "\n"
            self.cliques[key]["overlap"] = len([i for i in self.cliques[key]["members"] for j in all_nodes if i["id"] == j["id"]])

    def unique_list(self, l):
        ulist = []
        [ulist.append(x) for x in l if x not in ulist]
        return ulist

    def __get_keywords(self, text, features_dict):
        keywords = ""
        d = dict()
        for word in text:
            try:
                word = word.lower()
                if word.isalnum() or word.isdigit():
                    if features_dict[word] == 1:
                        d[word] += 1
            except KeyError:
                d[word] = 1   
                continue
        sorted_d = sorted(d.items(), key=operator.itemgetter(1), reverse=True)
        kw_count = 0
        for entry in sorted_d:
            if (kw_count < len(sorted_d) - 1) and (kw_count < 100):
                kw_count += 1
                keywords += (" | %s (%s) | " % (str(entry[0]), d[str(entry[0])]))
        logging.debug("Keywords found: %s" % keywords)
        return keywords

    def __create_html_results(self):
        logging.info("Generating HTML report")
        html_log = self.output_folder + "/results.html"
        csv_log = self.output_folder + "/results.csv"
        csv_string = "CliqueID\tSize\tOverlappingNodes\tFileID\tSiteID\tURL\tScriptID\tFilename\tDomains\tSource\n"
        page = html.HTML('html')
        page.script("",src="sorttable.js")
        page.p("List of Cliques")
        counter, bar_counter = 0, 0
        bar = progressbar.ProgressBar(maxval=max(1, len(self.cliques.keys())), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        for key in self.cliques.keys():
            bar_counter += 1
            bar.update(bar_counter)
            page.br
            clique_header_text = ("Clique # %s of %d " % (str(self.cliques[key]["id"]), len(self.cliques.keys())))
            page.text(clique_header_text)
            table = page.table(border='1', klass="sortable")
            row = table.tr(style="background-color:#FF0000")
            row.td("Clique ID")
            row.td("Size")
            row.td("Sample script")
            row.td("Clique Keywords")
            row.td("#Overlapping Members")
            row.td("N-1 Similar Cliques")
            row = table.tr
            row.td(str(self.cliques[key]["id"]))
            row.td(str(self.cliques[key]["size"]))
            random_member = random.choice(self.cliques[key]["members"])
            row.td.a("Sample script", href="../../../" + random_member["file"])
            row.td(str(self.cliques[key]["keywords"]))
            row.td(str(self.cliques[key]["overlap"]))
            row.td(str(self.cliques[key]["n-1-similar-cliques"]))
            subtable = page.table(border='1', klass="sortable")
            subrow = subtable.tr
            subrow.td("ID")
            subrow.td("Site #")
            subrow.td("Script #")
            subrow.td("URL")
            subrow.td("Script")
            subrow.td("Domains")
            subrow.td("Script Source")
            for node in self.cliques[key]["members"]:
                try:
                    string = ("%s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s" %(str(self.cliques[key]["id"]), str(self.cliques[key]["size"]), str(self.cliques[key]["overlap"]), str(node["id"]), str(node["site"]), str(node["url"]), str(node["script-id"]), str(node["file"]), str(node["domains"]), str(node["source"])))
                    csv_string += string + "\n" 
                    subrow = subtable.tr
                    subrow.td(str(node["id"]))
                    subrow.td(str(node["site"]))
                    subrow.td(str(node["script-id"]))
                    subrow.td(str(node["url"]))
                    subrow.td.a(str(node["file"]), href="../../../" + node["file"])
                    subrow.td(str(node["domains"]))
                    subrow.td(str(node["source"]))
                except Exception:
                    continue
        o = open(html_log, "w")
        o.write(str(page))
        o.flush()
        o.close()
        o = open(csv_log, "w")
        o.write(str(csv_string))
        o.flush()
        o.close()

