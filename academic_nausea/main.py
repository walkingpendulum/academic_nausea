import collections
import itertools
import multiprocessing
import os
import re
import traceback

import nltk.corpus as corpus
import transliterate
from nltk.stem.snowball import RussianStemmer

from .table import DatabaseHandler

ru_stemmer = RussianStemmer()
normalized_stopwords_set = set(map(ru_stemmer.stem, corpus.stopwords.words('russian')))
en_detector = re.compile(r"[A-Za-z]+")
ru_detector = re.compile(r"[А-Яа-я]+")


def detect_fraud(word, detectors=(en_detector, ru_detector)):
    """Проверяет отдельное слово чтобы количество использованных языков не превышало одного.

    Вообще говоря, такой подход пропускает слова, целиком написанные латиницей из букв, выглядящих похоже
    на кириллические, например слово "[много] TOBAPOB" подобный тест на мошенничество пройдет. С другой
    стороны, не представляется возможным определять мошенничество подобного рода без сверки со словарем
    русских слов. Такая проверка будет отнимать слишком много времени, причем теоретически возможны коллизии
    в обе стороны - слова, имеющие смысл в обоих написаниях (названия компаний, например), а так же аббревиатуры,
    которые в словарях не встречаются, но вполне возможны для использования.

    :param word: строка, которую проверяем на мошенничество.
    :param detectors: список детекторов -- скопилированных regex-матчеров
    :return: True если зафиксированно мошенничество
    """
    return sum(language_detector.search(word) is not None for language_detector in detectors) > 1


def _tokenize(file_descriptor):
    """Токенизатор, итерируется по отдельным словам в тексте.

    :param file_descriptor: file object or io.StringIO object
    :return:
    """

    def _tokenize_gen(string):
        yield from (x.group(0) for x in re.finditer(r"[A-Za-zА-Яа-я]+", string))

    yield from itertools.chain.from_iterable(_tokenize_gen(line) for line in file_descriptor)


def tokenize(path_to_file):
    """Обертка для токенизатора. Возвращает генератор, итерирующийся по отдельным словам в тексте.

    :param path_to_file:
    :return:
    """

    with open(path_to_file, encoding='utf=8') as f:
        yield from _tokenize(f)


def _process_document(word_generator):
    """ Обработка и подсчет тошноты по документу

    :param word_generator: iterable
    :return: словарь со структурой {'rate': float, 'fraud_words': set}
    """
    fraud_word_list = []
    normalized_word_list = []

    for word in word_generator:
        word = word.lower()
        if detect_fraud(word):
            # априори неизвестно, в какую сторону нужно нормализовывать слово с заменами, в
            # кириллицу или в латиницу. поэтому я провел небольшое исследование по всем текстовым
            # файлам, шедшим с заданием, и изучил список слов, в которых использовались буквы двух
            # алфавитов одновременно. выяснилось, что примерно из 1200 уникальных случаев мошенничества
            # количество исходно английских слов пренебрежимо мало (такие слова представляют собой
            # названия фирм или форматов/стандартов), поэтому было принято решение нормализовывать
            # всегда в сторону кирилицы.
            fraud_word_list.append(word)
            word = transliterate.translit(word, 'ru')

        normalized_word = ru_stemmer.stem(word)
        if normalized_word not in normalized_stopwords_set:
            normalized_word_list.append(normalized_word)

    counter = collections.Counter(normalized_word_list)
    total = sum(counter.values())
    if total:
        rate = (100 * sum(cnt for word, cnt in counter.most_common(5))) / total
    else:
        rate = 0.

    result = {
        'rate': rate,
        'fraud_words': set(fraud_word_list),
    }

    return result


def process_document(path_to_file):
    """ Обертка над обработкой и подсчетом тошноты по документу.

    :param path_to_file:
    :return: словарь вида {'rate': float, 'fraud_words': set, 'document_name': str} или None если произошла ошибка
    """
    word_generator = tokenize(path_to_file)

    try:
        result = _process_document(word_generator)
    except Exception:
        print('Something wrong, skip %s' % path_to_file)
        traceback.print_exc()
        return

    result['document_name'] = os.path.basename(path_to_file)
    return result


def calculate(path_to_file_list_or_str, database=None, table_name=None, processes=None):
    """ Обертка над полным циклом обработки: подсчет и сохранение в базу.

    :param path_to_file_list_or_str:
    :param database:
    :param table_name:
    :param processes: int
    :return:
    """
    if isinstance(path_to_file_list_or_str, str):
        path_to_file_list = [path_to_file_list_or_str]
    else:
        path_to_file_list = path_to_file_list_or_str

    processes = processes or multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=processes)
    documents = [x for x in pool.map(process_document, path_to_file_list) if x]

    db = DatabaseHandler(database=database, table_name=table_name)
    db.insert(documents)
