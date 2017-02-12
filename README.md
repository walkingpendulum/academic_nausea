# academic_nausea

Пакет для подсчета академической тошноты документа. На выходе выдает коэффициент тошноты (в процентах), а так же список слов, в которых была обнаружена попытка мошенничества. Если мошенничество в документе не было обнаружено, выводится None. 
## Установка пакета
```bash
$ pip install git+https://github.com/walkingpendulum/academic_nausea.git
Collecting git+https://github.com/walkingpendulum/academic_nausea.git
  Cloning https://github.com/walkingpendulum/academic_nausea.git to <...> 

< some stuff ... >

Installing collected packages: academic-nausea
  Running setup.py install for academic-nausea ... done
Successfully installed academic-nausea-0.0.1

$ nausea -h
usage: nausea [-h] [-d DATABASE] [--table TABLE] command

academic nausea computational routine

positional arguments:
  command

optional arguments:
  -h, --help            show this help message and exit
  -d DATABASE, --database DATABASE
                        database name to store result
  --table TABLE         table name to store result (default 'results')

Commands:
  calculate  calculate nausea rate for file
  list       list rates and metadata for all processed documents

Run nausea COMMAND --help for more information on a command.
```

## Запуск тестов
```bash
$ py.test tests/

```
## Примеры использования

### Как питонячий модуль
```python
from academic_nausea import calculate, DatabaseHandler

db_params = {'database': './database/test', 'table_name': 'results'}

calculate('/path/to/file', processes=2, **db_params)

db = DatabaseHandler(**db_params)
print(db.list_table('file name'))
```


##$ Как утилита командной строки (после установки через pip)

```bash
$ nausea --database `pwd`/database/test calculate --processes 2 $(ls /dir/with/files | grep txt)
<output>
$ nausea --database `pwd`/database/test list | tail -3
document name: 0998.txt -- rate: 16.35% -- fraud words: fiинтерфейс,gbпривод,mbжесткий,mbэкран,mhzоперативная,multiвидеокарта,картойvisa
document name: 0999.txt -- rate: 10.81% -- fraud words: None
document name: 1000.txt -- rate: 12.02% -- fraud words: None
```
Вывести три самых плохих записи относительно показателя academic nausea
```bash
$ nausea --database `pwd`/database/test list | sort -nk 6 | tail -3
document name: 0682.txt -- rate: 64.40% -- fraud words: None
document name: 0849.txt -- rate: 70.91% -- fraud words: None
document name: 0269.txt -- rate: 85.88% -- fraud words: None
```

Такой высокий показатель у лидера объясняется его содержанием
```bash
$ grep -v -e '^[" "]*$' 0269.txt | tail -10 | head -7
235 / 55 / 19 - от 3000 р/шт
245 / 40 / 19 - от 3500 р/шт
255 / 35 / 19 - от 3900 р/шт
255 / 40 / 19 - от 3100 р/шт
255 / 45 / 19 - от 3900 р/шт
255 / 50 / 19 - от 2700 р/шт
255 / 55 / 19 - от 4000 р/шт
```