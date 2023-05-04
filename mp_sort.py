import argparse
from pathlib import Path
import re
from shutil import unpack_archive
from multiprocessing import Pool, cpu_count

parser = argparse.ArgumentParser(description='Sorting folder')
parser.add_argument('--source', '-s', required=True, help='Source folder')
parser.add_argument('--output', '-o', default='sorted', help='Output folder')
args = vars(parser.parse_args())
source = args.get('source')
source = Path(source)
output = args.get('output')
output = source.parent.joinpath(output)


def recursive_iterdir(path: Path):
    """
    The recursive_iterdir function takes a pathlib.Path object as input and returns a list of all files in the directory
    and its subdirectories. It does this by first checking if the element is a directory, and if so, it calls itself on that
    directory to get all files within it. If not, then it appends that file to the result list.

    :param path: Specify the directory to be searched
    :return: A list of all files in the directory tree
    """
    result = []
    for element in path.iterdir():
        if element.is_dir():
            result.extend(recursive_iterdir(element))
        else:
            result.append(element)

    return result


def translator():
    """
    The translator function takes a string and returns a new string with all the Cyrillic characters replaced by their
    Latin equivalents. The function uses the zip() built-in to create a dictionary of Cyrillic characters as keys and
    their Latin equivalents as values. It then iterates over each character in the input string, checks if it is in
    the dictionary, and replaces it with its value if so.

    :return: A dictionary with the cyrillic symbols as keys and their latin equivalents as values
    """
    cyrillic_symbols = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    translation = (
        "a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
        "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")
    trans = {}
    for c, t in zip(cyrillic_symbols, translation):
        trans[ord(c)] = t
        trans[ord(c.upper())] = t.upper()

    return trans


def normalize(f_name):
    """
    The normalize function takes a string as an argument and returns the same string with all non-alphanumeric characters replaced by underscores.

    :param f_name: Pass in the name of a file
    :return: A string with all non-alphanumeric characters replaced by underscores
    """
    trans = translator()
    name = re.sub(r"\W+", "_", f_name)
    return name.translate(trans)


def sort(element):
    """
    The sort function takes a pathlib.Path object as an argument and sorts it into the appropriate folder in the output
    directory. The function first creates a dictionary of file types, with each key being a category (images, video, etc.)
    and each value being an array of extensions that belong to that category. It then normalizes the name of the file by
    removing all non-alphanumeric characters from its stem (the part before its extension). Next it gets rid of any leading
    or trailing periods in its extension and converts it to uppercase for easier comparison later on. Then we create new_name

    :param element: Pass the file or folder to be sorted
    :return: None
    """
    type_dict = {
        "images": ['JPEG', 'PNG', 'JPG', 'SVG'],
        "video": ['AVI', 'MP4', 'MOV', 'MKV'],
        "documents": ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
        "audio": ['MP3', 'OGG', 'WAV', 'AMR'],
        "archives": ['ZIP', 'GZ', 'TAR'],
        "other": []
    }

    new_stem = normalize(element.stem)
    extension = element.suffix.replace(".", "").upper()
    new_name = new_stem + "." + extension

    for key, value in type_dict.items():
        if extension in value:
            new_folder = output.joinpath(key)
            new_folder.mkdir(exist_ok=True, parents=True)
            if key == "archives":
                unpack_archive(element, new_folder.joinpath(new_stem))
                element.unlink()
                return
            else:
                element.rename(new_folder / new_name)
                return

    new_folder = output.joinpath("other")
    new_folder.mkdir(exist_ok=True)
    element.rename(new_folder / new_name)


def cleaner(path):
    """
    The cleaner function takes a pathlib.Path object as an argument and recursively deletes all empty directories within the given directory.

    :param path: Specify the directory to be cleaned
    :return: None
    """
    for item in path.iterdir():
        if item.is_dir():
            cleaner(item)
            if not any(item.iterdir()):
                item.rmdir()


if __name__ == '__main__':
    with Pool(cpu_count()) as pool:
        pool.map(sort, recursive_iterdir(source))
        pool.close()
        pool.join()

    cleaner(source)
    source.rmdir()
    print('Finished')
