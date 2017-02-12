import os
import subprocess

from .context import academic_nausea

path_to_file = os.path.join(os.path.dirname(__file__), 'text_files', '0998.txt')
path_to_lib = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
db_folder = os.path.join(path_to_lib, 'database')
db_path = os.path.join(db_folder, 'test')
if not os.path.exists(db_folder):
    os.makedirs(db_folder)


def test_lib_processing_file():

    academic_nausea.calculate(path_to_file, database=db_path)

    db = academic_nausea.DatabaseHandler(database=db_path)
    result, = db.list_table('0998.txt')

    assert result
    assert int(float(result['rate']) * 100) == 1635


def test_executable_processing_file():
    # здесь есть немного магии с путями и переменными окружения
    # она не нужна, если установить пакет через pip install (см. README)
    # но необходима, чтобы дотянуться до исполняемого файла и заставить
    # работать внутренние импорты без установки пакета

    prefix = 'PYTHONPATH=%s:$PYTHONPATH' % path_to_lib
    path_to_executable = os.path.join(path_to_lib, 'bin', 'nausea')
    _opts = [
        prefix,
        path_to_executable,
        '--database %s' % db_path,
    ]

    _calc_cmd = _opts + [
        'calculate',
        path_to_file
    ]
    output = subprocess.check_output([' '.join(_calc_cmd)], shell=True)
    print(output.decode())

    _list_cmd = _opts + [
        'list',
        '0998.txt',
    ]
    output = subprocess.check_output([' '.join(_list_cmd)], shell=True).strip().decode()
    right_result = (
        'document name: 0998.txt '
        '-- rate: 16.35% '
        '-- fraud words: fiинтерфейс,gbпривод,mbжесткий,mbэкран,mhzоперативная,multiвидеокарта,картойvisa'
    )
    assert output == right_result
