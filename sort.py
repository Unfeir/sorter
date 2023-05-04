import argparse
import pathlib
import re
from shutil import unpack_archive

parser = argparse.ArgumentParser(description='Sorting folder')
parser.add_argument('--source', '-s', required=True, help='Source folder')
args = vars(parser.parse_args())
source = args.get('source')
PATH = pathlib.Path(source)


def translator():
    """
    The translator function takes a string and returns a dictionary of the cyrillic symbols and their latin equivalents.
    The function is used in the 'translate' method to translate cyrillic strings into latin ones.

    :return: A dictionary with the cyrillic symbols as keys and their latin translation as values
    :doc-author: Trelent
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

    :param f_name: Pass the name of the file to be normalized
    :return: A string with all non-alphanumeric characters replaced by underscores
    """
    trans = translator()
    name = re.sub(r"\W+", "_", f_name)
    return name.translate(trans)


def recursive_iterdir(path):
    """
    The recursive_iterdir function takes a path as an argument and iterates through all the files in that directory.
    If it finds a subdirectory, it calls itself on that subdirectory. If not, it sorts the file.

    :param path: Specify the directory to be iterated through
    :return: None
    """
    for element in path.iterdir():
        if element.is_dir():
            recursive_iterdir(element)
        else:
            sort(element)


def sort(element):
    """
    The sort function takes a pathlib.Path object as an argument and sorts it into the appropriate folder
    based on its file extension. If the file is an archive, it will be unpacked into a new folder with the same name
    as the archive (without its extension) in a subfolder of &quot;archives&quot;. The original archive will then be deleted.

    :param element: Pass the file path to the sort function
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
            new_folder = PATH.joinpath(key)
            new_folder.mkdir(exist_ok=True)
            if key == "archives":
                unpack_archive(element, new_folder.joinpath(new_stem))
                element.unlink()
                return
            else:
                element.rename(new_folder / new_name)
                return

    new_folder = PATH.joinpath("other")
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


def main_fun():
    global PATH
    if PATH.is_dir():
        recursive_iterdir(PATH)
        cleaner(PATH)
    else:
        print(f"There is no such dir: {PATH}")


if __name__ == '__main__':
    main_fun()
    print("Finish")
