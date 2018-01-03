import logging
import extract_js
import argument_parser


def main():
    arguments = argument_parser.ArgumentParser()
    extractor = extract_js.ExtractJavascript(arguments.params)
    

if __name__ == '__main__':
    main()
