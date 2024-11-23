import pymorphy2
morph = pymorphy2.MorphAnalyzer()

def is_word_valid(word):
    parsed_word = morph.parse(word)[0]

    number = parsed_word.tag.number
    case = parsed_word.tag.case

    if pos == 'NOUN' and number == 'sing' and (case == 'nomn' or case == 'accs'):
        return True
    return False

