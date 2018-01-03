import logging
import argument_parser
import input_parser
import similarity_methods

def main():
    arguments = argument_parser.ArgumentParser()
    inputs = input_parser.InputFileParser(arguments.get_params())
    similarity = similarity_methods.SimilarityMethods(inputs.input_files, arguments.get_params())
    if arguments.method == "quick-difflib":
        similarity.difflib_quick_similarity_metric()
    elif arguments.method == "difflib":
        similarity.difflib_similarity_metric()
    elif arguments.method == "tfidf-cosine-full":
        similarity.tfidf_cosine_similarity_metric_fullcorpus()
    elif arguments.method == "tfidf-cosine-pair":
        similarity.tfidf_cosine_similarity_metric_paircorpus()


if __name__ == '__main__':
    main()
