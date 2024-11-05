import pymorphy2

morph = pymorphy2.MorphAnalyzer()
word = 'соль'


def is_word_valid(word):
    parsed_word = morph.parse(word)[0]
    # print(f"Нормальная форма: {parsed_word.normal_form}")
    pos = parsed_word.tag.POS
    number = parsed_word.tag.number
    case = parsed_word.tag.case
    if __name__ == '__main__':
        print(f"Часть речи: {pos}")
        print(f"Число: {number}")
        print(f"Падеж: {case}")

        print(f"Полное морфологическое описание: {parsed_word.tag}")
    if pos == 'NOUN' and number == 'sing' and (case == 'nomn' or case == 'accs'):
        return True
    return False


if __name__ == '__main__':
    print(is_word_valid(word))

'''
Нормальная форма: ананас
Часть речи: NOUN
Полное морфологическое описание: NOUN,inan,masc sing,nomn


'''
