import click
import os
from mp3_tagger import MP3File, VERSION_2

"""
Программа группирует файлы, анализируя ID3-теги по папкам:
<директория назначения>/<исполнитель>/<альбом>/<имя файла>.mp3.\n\r
Переименовывает файлы по схеме:
<название трека> - <исполнитель> - <альбом>.mp3.\n\r
Если в тегах нет информации о названии трека, использует оригинальное имя файла.\n\r
Если в тегах нет информации об исполнителе или альбоме, пропускает файл,
оставляя его без изменений в исходной директории.

Консольные команды:\n\r
--help - выводит справочное сообщение;\n\r
-s | --src-dir - исходная директория, по умолчанию директория в которой запущен скрипт;\n\r
-d | --dst-dir - целевая директория, по умолчанию директория в которой запущен скрипт.
"""


def check_src(src_dir):
    """Проверяет возможность перехода в исходный каталог

    src_dir: путь к исходному каталогу, тип str
    return: True, тип boolean

    Обрабатывает ошибки: FileNotFoundError, PermissionError

    """
    try:
        os.chdir(src_dir)
        return True
    except FileNotFoundError:
        click.echo(f'Каталог не найден: {src_dir}')
    except PermissionError:
        click.echo(f'Недостаточно прав на работу с каталогом: {src_dir}')


def check_dst(dst_dir):
    """Проверяет возможность перехода или налчие целевого каталога

    dst_dir: путь к исходному каталогу, тип str
    return: True, тип boolean

    Обрабатывает ошибки: FileNotFoundError, PermissionError

    """
    try:
        os.chdir(dst_dir)
        return True
    except FileNotFoundError:
        os.mkdir(dst_dir)
        return True
    except PermissionError:
        click.echo(f'Недостаточно прав на работу с каталогом: {dst_dir}')


def tag_cleaner(tag):
    """Удаляет из строки символы переноса строки, нулевые байты и пробелы с конца строки."""
    if tag:
        tag = tag \
            .replace("\n", "") \
            .replace("\r", "") \
            .rstrip('\x00') \
            .rstrip(' ') \
            .lstrip(' ')
    else:
        tag = None
    return tag


def mp3_files_list():
    """Формирует список .mp3 файлов текущей директории.

    return: список файлов, тип list.

    """
    files = os.listdir()
    mp3_files = []
    for i in files:
        if i.endswith('.mp3'):
            mp3_files.append(i)
    return mp3_files


def mp3_tags_list(mp3_file):
    """Формирует список тегов

    mp3_file: имя файла в текущей директории, тип str
    return: список тегов, тип list

    Обрабатывает ошибки: PermissionError

    """
    try:
        mp3 = MP3File(mp3_file)
        mp3.set_version(VERSION_2)
        artist = tag_cleaner(mp3.artist)
        album = tag_cleaner(mp3.album)
        song = tag_cleaner(mp3.song)
        return [artist, album, song]
    except PermissionError:
        click.echo(f'Недостаточно прав на работу с файлом: {mp3_file}')


def mp3_file_replace(mp3_file, old_path_name, new_path_name):
    """Перемещает или копирует с заменой .mp3 файлы из текущей в целевую директорию.

    mp3_file: имя файла в текущей директории, тип str;
    old_path_name: абсолютный путь к файлу в текущей директории, тип str;
    new_path_name: абсолютный путь к файлу в целевой директории, тип str.

    Обрабатывает ошибки: FileExistsError, OSError.

    """
    try:
        os.renames(old_path_name, new_path_name)
        click.echo(f'{old_path_name} -> {new_path_name}')
    except FileExistsError:
        os.replace(old_path_name, new_path_name)
        click.echo(f'{old_path_name} -> {new_path_name}')
    except OSError:
        click.echo(f'Ошибка при переименовании/перемещении файла: {mp3_file}')


def mp3_files_sort(mp3_files, src_dir, dst_dir):
    """Сортирует .mp3 файлы в целевую директорию по папкам

    mp3_files: список .mp3 файлов, тип list;
    src_dir: путь к исходной директории, тип str;
    dst_dir: путь к целевой директории, тип str.

    """
    for mp3_file in mp3_files:
        if mp3_tags_list(mp3_file):
            artist, album, song = mp3_tags_list(mp3_file)
            if artist and album:
                if song:
                    new_file_name = song + ' - ' + artist + ' - ' + album + '.mp3'
                else:
                    new_file_name = str(mp3_file)
                old_path_name = os.path.join(src_dir, mp3_file)
                new_path_name = os.path.join(dst_dir, artist, album, new_file_name)
                mp3_file_replace(mp3_file, old_path_name, new_path_name)
            else:
                click.echo(f'Альбом или исполнитель неизвестны в файле: {mp3_file}')


# Запуск консольного приложения
@click.command()
@click.option('-s', '--src-dir', default=os.getcwd(), help='source directory')
@click.option('-d', '--dst-dir', default=os.getcwd(), help='target directory')
def main_func(src_dir, dst_dir):
    """Программа для сортировки mp3 файлов по папкам."""

    if check_dst(dst_dir) and check_src(src_dir):
        mp3_files = mp3_files_list()
        mp3_files_sort(mp3_files, src_dir, dst_dir)


if __name__ == '__main__':
    main_func()
