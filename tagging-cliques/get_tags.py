import logging

class AssignTags:
	def __init__(self, params, cliques, scripts):
		self.cliques = cliques
		self.scripts = scripts
		self.output = params["input"]
		self.__assign_clique_tags()

	def __assign_clique_tags(self):
		output_script_tags = self.output + "/tags-by-script"
		output_clique_tags = self.output + "/tags-by-clique"
		for clique_id in self.cliques.keys():
			while self.cliques[clique_id]["tag"] is None:
				logging.info("Checking to see if we have a file in this clique whose tag we can inherit")
				tag_set = False
				for member in self.cliques[clique_id]["members"]:
					if self.scripts[member["file"]]["tag"] is not None:
						member["tag"] = self.scripts[member["file"]]["tag"]
						logging.info("Found a file (%s) that was already tagged as %s. Assigning that tag to the entire clique" % (member["file"], member["tag"]))
						self.cliques[clique_id]["tag"] = member["tag"]
						tag_set = True
						break
				if tag_set:
					continue
				logging.info("We need to assign a tag to clique ID: %s. Select a tag by pressing the corresponding number." % str(clique_id))
				logging.info("Available Tags: (1) AdBlock Detection, (2) Tracker, (3) UI, (4) Other, (5) Unidentified")
				tag = input("Select a tag (1-5): ")
				if tag == 1:
					self.cliques[clique_id]["tag"] = "AdBlockDetection"
				elif tag == 2:
					self.cliques[clique_id]["tag"] = "Tracker"
				elif tag == 3:
					self.cliques[clique_id]["tag"] = "UI"
				elif tag == 4:
					self.cliques[clique_id]["tag"] = "Other"
				elif tag == 5:
					self.cliques[clique_id]["tag"] = "Unidentified"
				else:
					logging.info("Invalid tag ID. Try again.")
					continue
			o = open(output_clique_tags, "a")
			string = str(clique_id) + "\t" + str(self.cliques[clique_id]["size"]) + "\t" + str(self.cliques[clique_id]["tag"]) + "\n"
			o.write(string)
			o.close()
			try:
				o = open(output_script_tags)
				lines = list()
				for line in o:
					lines.append(line.strip())
				o.close()
			except:
				lines = list()
			o = open(output_script_tags, "a")
			for member in self.cliques[clique_id]["members"]:
				member["tag"] = self.cliques[clique_id]["tag"]
				self.scripts[member["file"]]["tag"] = self.cliques[clique_id]["tag"]
				logging.info("File %s has been assigned the %s tag" % (member["file"], self.scripts[member["file"]]["tag"]))
				string = str(member["file"]) + "\t" + str(member["url"]) + "\t" + str(member["tag"]) + "\n"
				if string.strip() in lines:
					continue
				o.write(string)
			o.close()
