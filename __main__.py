from sys import argv, stderr

from imagesize import set_dimensions_for_filenames


if __name__ == '__main__':
    if len(argv) < 2:
        stderr.write('Directory path not passed')
        exit()

    _, directory = argv
    set_dimensions_for_filenames(directory)
