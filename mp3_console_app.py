import click
import os
# import logging
from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH


# logging.basicConfig(filename="info.log", level=logging.INFO)


def change_dir(dir_path):
    try:
        os.chdir(dir_path)
        return os.getcwd()
    except FileNotFoundError:
        click.echo(f'Каталог не найден: {dir_path}')
    except PermissionError:
        click.echo(f'Недостаточно прав на работу с каталогом: {dir_path}')


def mp3_files_list():
    files = os.listdir()
    mp3_files = []
    for i in files:
        if i.endswith('.mp3'):
            mp3_files.append(i)
    return mp3_files


def mp3_files_sort(mp3_files, dst_dir):
    src_dir = os.getcwd()
    for path_to_mp3 in mp3_files:
        try:
            with open(path_to_mp3, mode='rb+'):
                pass
        except PermissionError:
            click.echo(f'Недостаточно прав на работу с файлом: {path_to_mp3}')
            continue
        mp3 = MP3File(path_to_mp3)
        mp3.set_version(VERSION_2)
        if mp3.album and mp3.artist:
            if mp3.song:
                album = str(mp3.album)
                artist = str(mp3.artist)
                song = str(mp3.song)
                new_file_name = song + ' - ' + artist + ' - ' + album + '.mp3'
            else:
                new_file_name = str(path_to_mp3)
            old_path_name = os.path.join(src_dir, str(path_to_mp3))
            new_path_name = os.path.join(dst_dir, str(mp3.artist), str(mp3.album), new_file_name)
            click.echo(f'{path_to_mp3} -> {new_path_name}')
            # logging.info(f'{old_path_name}->{new_path_name};')
            try:
                os.renames(old_path_name, new_path_name)
            except OSError:
                click.echo(f'Синтаксическая ошибка в имени файла: {path_to_mp3}')
            except ValueError:
                click.echo(f'Некорректное значение пути к файлу: {path_to_mp3}')
        else:
            click.echo(f'Альбом или исполнитель неизвестны в файле: {path_to_mp3}')


# Запуск консольного приложения
@click.command()
@click.option('-s', '--src-dir', default=os.getcwd(), help='source directory')
@click.option('-d', '--dst-dir', default=os.getcwd(), help='target directory')
def func(src_dir, dst_dir):
    "Sort mp3 files artist -> album -> song"

    if change_dir(dst_dir) and change_dir(src_dir):
        mp3_files = mp3_files_list()
        mp3_files_sort(mp3_files, dst_dir)


if __name__ == '__main__':
    func()
