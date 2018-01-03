import os
import glob
import logging


class InputFileParser:
    def __init__(self, params):
        self.params = params
        logging.info("Getting all files in input folder: %s" % self.params["input"])
        self.input_files = dict()
        self.__get_input_files()

    def __get_input_files(self):
        count = 0
        for root, directories, filenames in os.walk(self.params["input"]):
            for filename in filenames:
                self.input_files[count] = os.path.join(root,filename)
                logging.debug("Added FileID: %d | File: %s " % (count, self.input_files[count]))
                count += 1
