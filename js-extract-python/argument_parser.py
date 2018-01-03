import logging
import argparse
import utils
import sys


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
        self.urls, self.dest, self.sim = args.url, args.store, float(args.sim)
        self.url_map = utils.load_url_index_dict(self.urls)
        self.minchars, self.maxchars = int(args.minchars), int(args.maxchars)
        utils.make_folder(self.dest)
        try:
            self.har = args.har
        except Exception:
            self.har = None
        try:
            self.html = args.html
        except Exception as ex:
            self.html = None
            logging.debug("Exception %s encountered while setting HAR source variable" % ex)
        self.__print_params()
        self.params = self.get_params()

    def __parse_args(print_help=False):
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug', '-d', help='Enable DEBUG level logging', action='store_true')
        parser.add_argument('-html', help='Folder containing HTML sources', dest='html')
        parser.add_argument('-har', help='Folder containing HAR sources', dest='har')
        parser.add_argument('-urls', help='List of URLs', dest='url')
        parser.add_argument('-dst', help='Folder which will contain extracted JS sources', dest='store', required=True)
        parser.add_argument('-minchars', help='Minimum number of non-whitespace chars in a JS for it to be considered', dest='minchars', required=True)
        parser.add_argument('-maxchars', help='Maximum number of non-whitespace chars in a JS before it has to be excluded', dest='maxchars', required=True)
        parser.add_argument('-sim', help='If a script from the same site has a similarity threshold higher than this value, it is excluded', dest='sim', required=True)
        parsed_args = parser.parse_args()
        return parsed_args

    def get_params(self):
        self.params = {"html": self.html, "har": self.har, "dst": self.dest, "urls": self.urls, "url-map": self.url_map, "sim": self.sim, "minchars": self.minchars, "maxchars": self.maxchars}
        return self.params

    def __print_params(self):
        logging.info("HTML Source: %s | HAR Source: %s | Urls: %s | Destination: %s | SimThreshold: %f | Min and Max chars: %s , %s" % (self.html, self.har, self.urls, self.dest, self.sim, self.minchars, self.maxchars))
