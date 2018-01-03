import glob
import argparse
import numpy
import progressbar


def parse_commandline():
    parser = argparse.ArgumentParser(description='Print adjacency matrix (combined)')
    parser.add_argument('--input_folder', dest='input', help='Folder containing npy matrices', required='True')
    args = parser.parse_args()
    return args


def print_matrix(matrix):
    string = ""
    for row in range(0, matrix.shape[0]):
        string += "\n"
        for col in range(0, matrix.shape[1]):
            string += ("[%d|%d] %f \t" % (row, col, matrix[row][col]))
    print string


def main():
    files = glob.glob(args.input + "/*.npy")
    matrices = list()
    bar = progressbar.ProgressBar(maxval=len(files), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    count = 0
    for f in files:
        count += 1
        matrices.append(numpy.load(f))
        bar.update(count)
    matrix = numpy.ones(matrices[0].shape) * -1
    bar = progressbar.ProgressBar(maxval=len(files) * matrix.shape[0] * matrix.shape[1] , widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    count = 0
    for m in matrices:
        for i in range(0, matrix.shape[0]):
            for j in range(0, matrix.shape[1]):
                count += 1
                matrix[i][j] = max(matrix[i][j], m[i][j])
                bar.update(count)
    numpy.set_printoptions(threshold=numpy.nan)
    print_matrix(matrix)

if __name__ == '__main__':
    args = parse_commandline()
    main()
