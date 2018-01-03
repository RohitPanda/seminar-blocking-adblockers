import logging
import argument_parser
import graph_analysis

def main():
    arguments = argument_parser.ArgumentParser()
    ga = graph_analysis.GraphAnalysis(arguments.get_params())

if __name__ == '__main__':
    main()
