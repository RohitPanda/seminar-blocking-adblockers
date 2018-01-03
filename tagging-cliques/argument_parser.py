import logging
import argparse

class ArgumentParser:
	def __init__(self):
		args = self.__parse_args()
		root = logging.getLogger()
		if root.handlers:
			for handler in root.handlers:
				root.removeHandler(handler)
		if args.debug:
			logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s', datefmt='%m-%d %H:%M')
			logging.info("Debug level logging enabled")
		else:
			logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s', datefmt='%m-%d %H:%M')
		self.input = args.input
		try:
			self.tagged = args.tags
		except:
			self.tagged = None
		self.params = {"input": self.input, "tags": self.tagged}
		self.__print_params()

	def __parse_args(self, print_help=False):
		parser = argparse.ArgumentParser()
		parser.add_argument('--debug', '-d', help='Enable DEBUG level logging', action='store_true')
		parser.add_argument('--result-folder', '-rf', help='Results Folder', dest='input', required=True)
		parser.add_argument('--tagged-scripts', '-t', help='File containing already tagged scripts', dest='tags')
		parsed_args = parser.parse_args()
		return parsed_args

	def __print_params(self):
		logging.info("Results Folder: %s | Tagged scripts: %s" % (self.input, self.tagged))


