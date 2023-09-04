import re
import argparse
from pathlib import Path
import shutil

CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", "ja", "je", "ji", "g")
TRANS = {ord(c): l for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION)}

def normalize(name: str) -> str:
    t_name = name.translate(TRANS)
    t_name = re.sub(r'\W', '_', t_name)
    return t_name

def handle_media(filename: Path, target_folder: Path) -> None:
    target_folder.mkdir(exist_ok=True, parents=True)
    new_name = normalize(filename.stem) + filename.suffix
    filename.replace(target_folder / new_name)

def handle_other(filename: Path, target_folder: Path) -> None:
    target_folder.mkdir(exist_ok=True, parents=True)
    new_name = normalize(filename.stem) + filename.suffix
    filename.replace(target_folder / new_name)

def handle_archive(filename: Path, target_folder: Path) -> None:
    target_folder.mkdir(exist_ok=True, parents=True)
    folder_for_file = target_folder / normalize(filename.stem)
    folder_for_file.mkdir(exist_ok=True)
    try:
        shutil.unpack_archive(str(filename), str(folder_for_file))
    except shutil.ReadError:
        print('It is not an archive')
        folder_for_file.rmdir()
    filename.unlink()

def get_extension(filename: str) -> str:
    return Path(filename).suffix[1:].upper()

def scan(folder: Path) -> None:
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'MY_OTHER'):
                FOLDERS.append(item)
                scan(item)
            continue
        ext = get_extension(item.name)
        fullname = folder / item.name
        if not ext:
            MY_OTHER.append(fullname)
        else:
            try:
                container = REGISTER_EXTENSION[ext]
                EXTENSION.add(ext)
                container.append(fullname)
            except KeyError:
                UNKNOWN.add(ext)
                MY_OTHER.append(fullname)

def read_folder(path: Path, output_folder: Path) -> None:
    for el in path.iterdir():
        if el.is_dir():
            read_folder(el, output_folder)
        else:
            copy_file(el, output_folder)

def copy_file(file: Path, output_folder: Path) -> None:
    ext = file.suffix
    new_path = output_folder / ext
    new_path.mkdir(exist_ok=True, parents=True)
    shutil.copyfile(str(file), str(new_path / file.name))

def main():
    parser = argparse.ArgumentParser(description='Sorting folder')
    parser.add_argument('--source', '-s', required=True, help='Source folder')
    parser.add_argument('--output', '-o', default='dist', help='Output folder')
    args = parser.parse_args()
    source = args.source
    output = args.output

    output_folder = Path(output)
    folder_for_scan = Path(source)  # Оголошення folder_for_scan
    read_folder(folder_for_scan, output_folder)

    print(f'Start in folder: {folder_for_scan.resolve()}')

    scan(folder_for_scan)
    for file in JPEG_IMAGES:
        handle_media(file, folder_for_scan / 'images' / 'JPEG')
    for file in JPG_IMAGES:
        handle_media(file, folder_for_scan / 'images' / 'JPG')
    for file in PNG_IMAGES:
        handle_media(file, folder_for_scan / 'images' / 'PNG')
    for file in SVG_IMAGES:
        handle_media(file, folder_for_scan / 'images' / 'SVG')
    for file in MP3_AUDIO:
        handle_media(file, folder_for_scan / 'audio' / 'MP3')
    for file in MY_OTHER:
        handle_other(file, folder_for_scan / 'MY_OTHER')
    for file in ARCHIVES:
        handle_archive(file, folder_for_scan / 'ARCHIVES')
    for folder in FOLDERS[::-1]:
        try:
            folder.rmdir()
        except OSError:
            print(f"Can't delete folder: {folder_for_scan}")


JPEG_IMAGES = []
JPG_IMAGES = []
PNG_IMAGES = []
SVG_IMAGES = []
MP3_AUDIO = []
MY_OTHER = []
ARCHIVES = []
FOLDERS = []
EXTENSION = set()
UNKNOWN = set()
REGISTER_EXTENSION = {
    'JPEG': JPEG_IMAGES,
    'JPG': JPG_IMAGES,
    'PNG': PNG_IMAGES,
    'SVG': SVG_IMAGES,
    'MP3': MP3_AUDIO,
    'AVI': [],
    'MP4': [],
    'MOV': [],
    'MKV': [],
    'DOC': [],
    'DOCX': [],
    'TXT': [],
    'PDF': [],
    'XLSX': [],
    'PPTX': [],
    'ZIP': ARCHIVES,
    'GZ': [],
    'TAR': []
}

if __name__ == "__main__":
    main()
