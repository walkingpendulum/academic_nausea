from .context import academic_nausea
from io import StringIO


def test_empty_input():
    text = StringIO("")
    word_gen = academic_nausea.main._tokenize(text)
    result = academic_nausea.main._process_document(word_gen)

    assert int(result['rate']) == 0
    assert result['fraud_words'] == set()


def test_5_words_document():
    _text = '''
        ▒▒▒▒ машина автомобиль автобус самолет паровоз ➔➔➔➔▒▒▒▒▒▒▒▒▒▒
    '''
    text = StringIO(_text)
    word_gen = academic_nausea.main._tokenize(text)
    result = academic_nausea.main._process_document(word_gen)

    assert int(result['rate']) == 100
    assert result['fraud_words'] == set()


def test_long_nauseating_document():
    _text = '''
        ▒▒▒▒ %s нaш тoвар Bоsch по сaмым низkим ценaм тoлько cейчас и cегодня ➔➔➔➔▒▒▒▒▒▒▒▒▒▒
    ''' % ('покупaй ' * 93, )
    text = StringIO(_text)

    word_gen = academic_nausea.main._tokenize(text)
    result = academic_nausea.main._process_document(word_gen)

    assert int(result['rate']) == 97
    fraud_words_set = {'bоsch', 'сaмым', 'покупaй', 'нaш', 'ценaм', 'тoлько', 'cегодня', 'cейчас', 'низkим', 'тoвар'}
    assert result['fraud_words'] == fraud_words_set
