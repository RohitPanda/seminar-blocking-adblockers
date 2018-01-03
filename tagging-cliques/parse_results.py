import logging

class ResultParser:
	def __init__(self, params):
		self.file =  params["input"]
		self.tags = {}
		if params["tags"] is not None:
			f = open(params["tags"])
			for line in f:
				line = line.split("\t")
				self.tags[line[0].strip()] = line[2].strip()
				print ("File %s: %s" %(line[0].strip(), self.tags[line[0].strip()]))
		self.cliques = dict()
		self.scripts = dict()
		self.__get_clique_dictionary()
		#print "Cliques: ", self.cliques
		#print "Scripts: ", self.scripts

	def __get_clique_dictionary(self):
		f = open(self.file+"/results.csv")
		for line in f:
			if "CliqueID" in line:
				continue
			line = line.split("\t")
			clique_id, clique_size, clique_ol_nodes = int(line[0]), int(line[1]), int(line[2])
			member_id, member_site, member_url, member_script, member_file, member_domains, member_source = int(line[3]), int(line[4]), line[5], int(line[6]), line[7].split("/")[-1].strip(), line[8], line[9]
			member = {"id": member_id, "site": member_site, "url": member_url, "script": member_script, "file": member_file.strip(), "domains": member_domains, "source": member_source, "tag": None}
			try:
				self.cliques[clique_id]["size"] = clique_size
				self.cliques[clique_id]["overlapping-nodes"] = clique_ol_nodes
				self.cliques[clique_id]["members"].append(member)
				self.cliques[clique_id]["tag"] = None
			except KeyError:
				self.cliques[clique_id] = {"size": clique_size, "overlapping-nodes": clique_ol_nodes, "members": list(), "tag": None}
			try:
				self.scripts[member_file]["id"] = member_id
				self.scripts[member_file]["site"] = member_site
				self.scripts[member_file]["url"] = member_url
				self.scripts[member_file]["domains"] = member_domains
				self.scripts[member_file]["source"] = member_source
				try:
					self.scripts[member_file]["tag"] = self.tags[member_file]
				except:
					self.scripts[member_file]["tag"] = None
				self.scripts[member_file]["cliques"].append(clique_id)
			except KeyError:
				try:
					tag = self.tags[member_file]
				except:
					tag = None
				self.scripts[member_file] = {"id": member_id, "site": member_site, "url": member_url, "domains": member_domains, "source": member_source, "tag": tag, "cliques": list()}
