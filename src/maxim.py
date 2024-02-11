'''

с. В названии нормативного правого акта не допускается перенос слов.

   т. Заголовки глав, разделов, частей, параграфов и подразделов отделяются от предыдущего текста двумя межстрочными
   интервалами, а от последующего текста - одним.
   (только в формате .docx ????)

   у. При ссылке на абзацы, строки и предложения их нумерация обозначается порядковыми числительными (прописью),
   при этом ссылка на абзац производится обозначением словом "абзац".

   ф. В тексте нормативного правового акта ссылка на пункт, подпункт приводится с указанием их порядкового номера
   (для их обозначения не допускается использование прилагательных).

   х. Если в нормативном правовом акте имеется ссылка на приложение, то указывается номер данного приложения,
   за исключением случаев, когда к нормативному правовому акту имеется одно приложение.

'''
import re

LAW_NAMES = ['конституция', 'закон', 'кодекс', 'постановление', 'приказ']

with open('z2300000013.29-06-2023.rus.txt', 'r', encoding='UTF-8') as file:
    data = file.readlines()
PATTERN_PAR = r'абзац[а-я]*'
PATTERN_PART = r'\bчасть\b|\bчасти\b|\bчастью\b'
PATTERN_POINT = r'\bпунк[а-я]*'
PATTERN_SUBPOINT = r'\bподпункт\b|\bподпункта\b'
POINT_NUM = r'[0-9]*\b'
POINT_SUB = r'[0-9]*\)'
# Шаблон для цифровых значений прописью
CURSIVE = (r'перв[а-я]*|втор[а-я]*|трет[а-я]*|четверт[а-я]*|пят[а-я]*|'
           r'шесто[а-я]*|седь[а-я]|восьм[а-я]*|девят[а-я]*|десят[а-я]*|'
           r'одинадцат[а-я]*|двенадцат[а-я]*|тринадцат[а-я]*|четырнадц[а-я]*|'
           r'пятнадцат[а-я]*|шестнадцат[а-я]*|семнадцат[а-я]*|восемнадцат[а-я]*|'
           r'девятнадцат[а-я]*|двадцат[а-я]*|тридцат[а-я]*|сорок[а-я]*')

APPENDIX = r'приложени[а-я]*'
APPENDIX_CHECK_1 = r'\bк\b'
APPENDIX_CHECK_2 = r'настоящ[а-я]*'


def is_word_wrapping(text: list['str']) -> bool:
    """
    Function check words wrapping in text header
    :param text:
    :return: True|False
    """
    header = []
    for item in text:
        if item.strip():
            start = item.lower().split()[0]
            if start in LAW_NAMES:
                break
            else:
                header.append(item.strip())
    for item in header:
        if item.endswith('-') or item.endswith(' -'):
            return False
    return True


def is_true_link_num(text: list[str], idx: int) -> dict[str:bool]:
    """
    Функция проверяет, что в строке текста перед порядковым
    номером прилагательного находится слово "абзац" или "часть"
    :param text:
    :param idx:
    :return:
    """
    result = {}
    check = ((text[idx].strip().replace(' и ', ' ')
              .replace('–', ' '))
             .replace(',', ' ').split())

    for i in range(len(check)):
        if re.match(CURSIVE, check[i].lower()):
            if i == 0 and (re.match(PATTERN_PAR, text[idx - 1][-1].lower())
                           or re.match(PATTERN_PART, text[idx - 1][-1].lower())):
                result[' '.join(check)] = True
            elif re.match(PATTERN_PAR, check[i - 1].lower()) or re.match(PATTERN_PART, check[i - 1].lower()):
                result[' '.join(check)] = True
            elif re.match(CURSIVE, check[i - 1].lower()):
                for j in range(1, i + 1):
                    if re.match(CURSIVE, check[i - j].lower()):
                        continue
                    elif re.match(PATTERN_PAR, check[i - j].lower()) or re.match(PATTERN_PART, check[i - j].lower()):
                        result[' '.join(check)] = True
            else:
                result[' '.join(check)] = False
    return result


def is_cursive_num_after_par(text: list[str], idx: int) -> dict[str:bool]:
    """
    Функция проверяет, что после слов "абзац", "часть" нумерация обозначается прописью
    :param text:
    :param idx:
    :return:
    """
    result = {}
    check = ((text[idx].strip().replace(' и ', ' ')
              .replace('–', ' '))
             .replace(',', ' ').split())
    for i in range(len(check)):
        if re.match(PATTERN_PAR, check[i].lower()) or re.match(PATTERN_PART, check[i].lower()):
            if i == len(check) - 1 and (re.match(CURSIVE, text[idx + 1][0].lower())):
                result[' '.join(check)] = True
            elif re.match(CURSIVE, check[i + 1].lower()):
                result[' '.join(check)] = True
            else:
                result[' '.join(check)] = False
    return result


def is_paragraph_link_numeration(text: list['str']) -> list:
    """
    Function check paragraph link numeration is in cursive
        :param text:
        :return: True|False
        """
    result = []
    flag = appendix_flag(text)
    # Проверяем строки, которые соответсвуют шаблону CURSIVE
    for i in range(len(text)):
        if re.search(CURSIVE, text[i].lower()):
            result.append(is_true_link_num(text, i))
        if re.search(PATTERN_PAR, text[i].lower()) or re.search(PATTERN_PART, text[i].lower()):
            result.append(is_cursive_num_after_par(text, i))
        if re.search(PATTERN_POINT, text[i].lower()):
            result.append(is_point_numeration(text, i))
        if re.search(PATTERN_SUBPOINT, text[i].lower()):
            result.append(is_sub_point_numeration(text, i))
        if re.search(APPENDIX, text[i].lower()):
            result.append(appendix_check(text, i, flag))

    return result


def is_point_numeration(text: list[str], idx: int) -> dict[str:bool]:
    """
    Функция проверяет, что после слова "пункт" правильная нумерация
    :param text:
    :param idx:
    :return:
    """
    result = {}
    check = ((text[idx].strip().replace(' и ', ' ')
              .replace('–', ' '))
             .replace(',', ' ').split())
    for i in range(len(check)):
        if re.match(PATTERN_POINT, check[i].lower()):
            if i == len(check) - 1:
                if re.match(POINT_NUM, text[idx + 1][0].lower()):
                    result[' '.join(check)] = True
                else:
                    result[' '.join(check)] = False
                break
            elif re.match(POINT_NUM, check[i + 1]):
                result[' '.join(check)] = True
            else:
                result[' '.join(check)] = False

    return result


def is_sub_point_numeration(text: list[str], idx: int) -> dict[str:bool]:
    result = {}
    check = ((text[idx].strip().replace(' и ', ' ')
              .replace('–', ' '))
             .replace(',', ' ').split())
    for i in range(len(check)):
        if re.match(PATTERN_SUBPOINT, check[i].lower()):
            if i == len(check) - 1:
                if re.match(POINT_SUB, text[idx + 1][0].lower()):
                    result[' '.join(check)] = True
                else:
                    result[' '.join(check)] = False
                break
            elif re.match(POINT_SUB, check[i + 1]):
                result[' '.join(check)] = True
            else:
                result[' '.join(check)] = False
    return result


def appendix_flag(text: list[str]):
    flag_list = [0]
    for i in range(len(text)):
        if re.search(APPENDIX, text[i].lower()):
            check = ((text[i].strip().replace(' и ', ' ')
                      .replace('–', ' '))
                     .replace(',', ' ').split())
            flag = 2 if len(check) == 2 else 1 if len(check) == 1 else 0
            flag_list.append(flag)
    return max(flag_list)


def appendix_check(text: list[str], idx: int, flag: int) -> dict[str:bool]:
    result = {}
    check = ((text[idx].strip().replace(' и ', ' ')
              .replace('–', ' '))
             .replace(',', ' ').split())
    if flag == 0:
        return result
    for i in range(len(check)):
        if flag == 2:
            if re.match(APPENDIX, check[i].lower()) and re.match(APPENDIX_CHECK_1, check[i + 1].lower()) \
                    and re.match(APPENDIX_CHECK_2, check[i + 2].lower()):
                result[' '.join(check)] = False
            else:
                result[' '.join(check)] = True
        elif flag == 1:
            if re.match(APPENDIX, check[i].lower()) and re.match(POINT_NUM, check[i + 1]):
                result[' '.join(check)] = False
            else:
                result[' '.join(check)] = True
    return result


if __name__ == '__main__':
    # print(is_word_wrapping(data))
    res = is_paragraph_link_numeration(data)
    for item in res:
        for k, v in item.items():
            if not v:
                print(k)
                print(v)
