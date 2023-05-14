# NB!
# libffi libheif must be installed in OS to make pi_heif/pyheif work.

from os.path import splitext
from pathlib import Path
from re import VERBOSE, compile as re_compile
from sys import stdout, stderr

from PIL import Image, UnidentifiedImageError
from pi_heif import register_heif_opener


IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff', '.heic'}
IMAGE_FORMATS = ('JPEG', 'HEIF', 'PNG', 'WEBP', 'TIFF')
SIZED_IMAGE_FILENAME_PATTERN = re_compile(r'''
    ^(?P<base>.+)  # base, e.g. istanbul/IMG_1850
    \.(?P<width>\d+)x(?P<height>\d+)$  # {width}x{height}, e.g. 800x600
''', flags=VERBOSE, )
register_heif_opener()


def set_dimensions_for_filenames(path: str) -> None:
    processed = 0

    directory_path = Path(path)
    if not directory_path.is_dir():
        stderr.write(f'{path} is not a directory\n')
        exit()

    files = filter(lambda f: not f.name.startswith('.'), directory_path.glob('*'))
    for file in files:
        file.resolve()
        if not file.is_file():
            stderr.write(f'{file} cannot be read\n')
            continue

        if file.suffix not in IMAGE_SUFFIXES:
            stderr.write(f'{file} not supported\n')
            continue

        width, height = _get_dimensions_from_image_file(file)
        if not all((width, height)):
            continue

        _rename_file_with_dimensions(file, width, height)
        processed += 1

    stdout.write(f'Processed {processed} images.\n')


def _get_dimensions_from_image_file(file: Path) -> tuple[int, int]:
    try:
        image = Image.open(file, formats=IMAGE_FORMATS)  # noqa
    except UnidentifiedImageError:
        stderr.write(f'Image not recognized: {file}\n')
        return 0, 0
    return image.size


def _rename_file_with_dimensions(file: Path, width: int, height: int) -> Path:
    basename, ext = splitext(file)
    # Image dimensions already set in filename, update
    match = SIZED_IMAGE_FILENAME_PATTERN.match(basename)
    if match is not None:
        basename = match.group('base')
    sized_filename = f'{basename}.{width}x{height}{ext}'
    sized_filename_path = Path(sized_filename)
    return file.rename(sized_filename_path)
