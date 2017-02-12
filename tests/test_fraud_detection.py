from .context import academic_nausea
from io import StringIO


def test_simple_good_1():
    hello_ru = academic_nausea.detect_fraud('привет')
    assert hello_ru is False


def test_simple_good_2():
    hello_en = academic_nausea.detect_fraud('hello')
    assert hello_en is False


def test_advanced_good():
    good_mixed_text = StringIO('техника bosch лучшая')
    good_mixed_text_results = []
    for word in academic_nausea.main._tokenize(good_mixed_text):
        good_mixed_text_results.append(academic_nausea.detect_fraud(word))
    assert all(flag is False for flag in good_mixed_text_results)


def test_advanced_bad():
    bad_mixed_text = StringIO('тexникa bоsсh лучшaя')
    bad_mixed_text_results = []
    for word in academic_nausea.main._tokenize(bad_mixed_text):
        bad_mixed_text_results.append(academic_nausea.detect_fraud(word))
    assert all(flag is True for flag in bad_mixed_text_results)
