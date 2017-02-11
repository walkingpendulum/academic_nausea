import collections
import itertools
import multiprocessing
import os
import re

import nltk.corpus as corpus
import transliterate
from nltk.stem.snowball import RussianStemmer

from .table import DatabaseHandler


ru_stemmer = RussianStemmer()
normalized_stopwords_set = set(map(ru_stemmer.stem, corpus.stopwords.words('russian')))
en_detector = re.compile(r"[A-Za-z]+")
ru_detector = re.compile(r"[А-Яа-я]+")


def detect_fraud(string, detectors=(en_detector, ru_detector)):
    """Проверяет чтобы количество используемых языков в строке не превышало одного

    :param string:
    :param detectors:
    :return:
    """
    return sum(language_detector.search(string) is not None for language_detector in detectors) > 1


def tokenize(path_to_file):
    """Возвращает генератор, итерирующийся по отдельным словам в тексте

    :param path_to_file:
    :return:
    """

    def _tokenize(string):
        yield from (x.group(0) for x in re.finditer(r"[A-Za-zА-Яа-я]+", string))

    with open(path_to_file) as f:
        yield from itertools.chain.from_iterable(_tokenize(line) for line in f)


def process_document(path_to_file):
    fraud_word_list = []
    normalized_word_list = []

    for word in tokenize(path_to_file):
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
        rate = None

    result = {
        'document_name': os.path.basename(path_to_file),
        'rate': rate,
        'fraud_words': set(fraud_word_list),
    }
    return result


def calculate(path_to_file_list, database_name, table_name=None, processes=None):
    db = DatabaseHandler(db_name=database_name, table_name=table_name)
    db.create_table_if_not_exist()

    processes = processes or multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=processes)
    documents = pool.map(process_document, path_to_file_list)
    map(db.insert_document, documents)


if __name__ == '__main__':
    path_prefix = os.path.join(os.path.dirname(__file__))
    files_dir_path = os.path.join(path_prefix, 'text_files')

    file_path_list = [os.path.join(files_dir_path, x) for x in os.listdir(files_dir_path) if x.endswith('.txt')]
    calculate(file_path_list, database_name='test')
