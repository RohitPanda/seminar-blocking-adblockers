import argument_parser
import parse_results
import get_tags

def main():
	arguments = argument_parser.ArgumentParser()
	results = parse_results.ResultParser(arguments.params)
	tags = get_tags.AssignTags(arguments.params, results.cliques, results.scripts)

if __name__ == '__main__':
	main()
