import re
from docx import Document
import json
import traceback


def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)


def remove_footnotes(text):
    # Регулярное выражение для поиска абзацев, начинающихся с "Сноска." и заканчивающихся точкой с пробелом,
    # за исключением случаев с сокращениями типа "см." и "ст."
    pattern = r"Сноска\..*?(?<!см)(?<!ст)\.\s"
    cleaned_text = re.sub(pattern, "", text, flags=re.DOTALL)

    pattern_izpi = r"Примечание ИЗПИ!\n\n\s*.*?(?=ОБЩАЯ ЧАСТЬ|РАЗДЕЛ 1|\n\n)"

    # Используем re.DOTALL, чтобы точка соответствовала переносам строки
    cleaned_text = re.sub(pattern_izpi, "", cleaned_text, flags=re.DOTALL)

    return cleaned_text


def segment_pdf_text_across_pages(full_text):
    chapter_pattern = re.compile(
        r'(Глава \d+\..*?)(?=Глава \d+\.|$)', re.DOTALL)
    article_pattern = re.compile(
        r'(Статья \d+(?:-\d+)?\..*?)(?=Статья \d+(?:-\d+)?\.|$)', re.DOTALL)

    chapters = [{'title': m.group(1).split('\n', 1)[0], 'content': m.group(
        1)} for m in chapter_pattern.finditer(full_text)]
    articles = [{'title': m.group(1).split('\n', 1)[0], 'content': m.group(
        1)} for m in article_pattern.finditer(full_text)]

    return chapters, articles

# проверка пунктуации глав


def check_chapter_punctuation(chapters):
    pattern = re.compile(r"^Глава\s[0-9]{1,2}\.\s.*")
    error_type = ''
    for i in range(len(chapters)):
        match = re.match(pattern, chapters[i]['title'])
        if not match:
            print(f"error at {chapters[i]['title']}")
            error_type = 'Пунктуация названия глав нарушена'
            error = {
                "error_type": error_type,
                "error_text": chapters[i]['title'],
                "start": -1,
                "end": -1,
            }
            errors.append(error)


# Проверка пунктуации статей
def check_article_punctuation(articles):
    pattern = re.compile(r"^Статья\s[0-9]{1,3}\-{0,1}[0-9]{0,2}\..*")
    for i in range(len(articles)):
        match = re.findall(pattern, articles[i]['title'])
        if len(match) == 0:
            print(f"error at {articles[i]['title']}")
            error_type = 'Пунктуация названия статей нарушена'
            error = {
                "error_type": error_type,
                "error_text": articles[i]['title'],
                "start": -1,
                "end": -1,
            }
            errors.append(error)


# Проверка на нумерацию глав
def check_numeration_chapter(chapters):
    last_num = 0
    is_special = False

    for i in range(len(chapters)):
        try:
            expression = re.compile(r'[0-9]{1,2}\-{0,1}[0-9]{0,2}')
            expression1 = re.compile(r'[0-9]{1}\-{0,1}[0-9]{0,2}')
            expression2 = re.compile(r'[0-9]{2}\-{0,1}[0-9]{0,2}')
            match = re.findall(expression, chapters[i]['title'][6:8])
            match1 = re.findall(expression1, chapters[i]['title'][6:8])
            match2 = re.findall(expression2, chapters[i]['title'][6:8])
            if len(match[0]) > 2:
                if len(match2) > 0:
                    num = int(match[0][:2])
                    is_special = True
                elif len(match1) > 0:
                    num = int(match[0][:1])
                    is_special = True
            else:
                num = int(match[0])
                is_special = False
        except ValueError:
            return False

        # print(last_num) , print(num)
        if is_special:
            if num != last_num:
                print(f"error at {chapters[i]['title']}")
                error_type = 'Нарушена нумерация глав'
                error = {
                    "error_type": error_type,
                    "error_text": chapters[i]['title'],
                    "start": -1,
                    "end": -1,
                }
                errors.append(error)
                return False
        else:
            if num != last_num + 1:
                print(f"error at {chapters[i]['title']}")
                error_type = 'Нарушена нумерация глав'
                error = {
                    "error_type": error_type,
                    "error_text": chapters[i]['title'],
                    "start": -1,
                    "end": -1,
                }
                errors.append(error)
                return False
        last_num = num
        # print("========")

    return True


# Проверка на нумерацию статей
def check_numeration_article(articles):
    last_num = 0
    is_special = False

    for i in range(len(articles)):
        try:
            expression = re.compile(r'[0-9]{1,2}\-{0,1}[0-9]{0,2}')
            expression1 = re.compile(r'[0-9]{1}\-{0,1}[0-9]{0,2}')
            expression2 = re.compile(r'[0-9]{2}\-{0,1}[0-9]{0,2}')
            match = re.findall(expression, articles[i]['title'][7:14])
            match1 = re.findall(expression1, articles[i]['title'][7:14])
            match2 = re.findall(expression2, articles[i]['title'][7:14])
            if len(match[0]) > 2:
                if len(match2) > 0:
                    num = int(match[0][:2])
                    is_special = True
                elif len(match1) > 0:
                    num = int(match[0][:1])
                    is_special = True
            else:
                num = int(match[0])
                is_special = False
        except ValueError:
            return False

        # print(last_num) , print(num)
        if is_special:
            if num != last_num:
                print(f"error at {articles[i]['title']}")
                error_type = 'Нарушена нумерация статей'
                error = {
                    "error_type": error_type,
                    "error_text": articles[i]['title'],
                    "start": -1,
                    "end": -1,
                }
                errors.append(error)
                return False
        else:
            if num != last_num + 1:
                print(f"error at {articles[i]['title']}")
                error_type = 'Нарушена нумерация статей'
                error = {
                    "error_type": error_type,
                    "error_text": articles[i]['title'],
                    "start": -1,
                    "end": -1,
                }
                errors.append(error)
                return False
        last_num = num
        # print("========")

    return True


# Проверка на пунктуацию пунктов/подпунктов


def check_seq(articles, k):
    pre_lines = articles[k]['content'].split('\n')

    lines = [line.strip() for line in pre_lines if line.strip()]

    pattern = re.compile(r'^[0-9]')
    pattern1 = re.compile(r'^[0-9]+\)\s{1}')
    pattern2 = re.compile(r'^[0-9]+\.\s')
    pattern3 = re.compile(r'^[А-Яа-я]+')
    pattern4 = re.compile(r'^[0-9]{1,2}\-{1}[0-9]{1,2}\.\s')
    pattern5 = re.compile(r'^[0-9]{1,2}\-{1}[0-9]{1,2}\)')
    pattern6 = re.compile(r'^[А-Я]+.+\:$')

    matches_pattern = []
    matches_pattern1 = []
    matches_pattern5 = []
    matches_pattern4 = []
    no_num_matches = []

    first_line_matches = list(re.finditer(pattern, lines[1]))

    if len(first_line_matches) > 0:
        for i in range(1, len(lines)):
            match_found = False
            for match in re.finditer(pattern3, lines[i]):
                if len(match.group()) > 0:
                    match_found = True
                    continue
            for match in re.finditer(pattern4, lines[i]):
                if len(match.group()) > 0:
                    match_found = True
                    # matches_pattern.append(match.group())
                    matches_pattern4.append(match.group())
            for match in re.finditer(pattern2, lines[i]):
                matches_pattern.append(match.group())
                match_found = True
            for match in re.finditer(pattern5, lines[i]):
                matches_pattern5.append(match.group())
                match_found = True
            for match in re.finditer(pattern6, lines[i]):
                no_num_matches.append(match.group()[:1])
                # match_found = True
            else:
                for match in re.finditer(pattern1, lines[i]):
                    matches_pattern1.append(match.group())
                    match_found = True

            if match_found == False:
                print(f"error at {articles[k]['title']} ")
                error_type = 'Нарушена пунктуация подпункта/подпункта'
                error = {
                    "error_type": error_type,
                    "error_text": [articles[i]['title'], lines[i]],
                    "start": -1,
                    "end": -1,
                }
                errors.append(error)
                # print(lines[i])
                # print("=====111")
    else:
        for i in range(2, len(lines)):
            match_found = False
            for match in re.finditer(pattern3, lines[i]):
                if len(match.group()) > 0:
                    match_found = True
                    continue
            for match in re.finditer(pattern4, lines[i]):
                if len(match.group()) > 0:
                    match_found = True
                    continue
            for match in re.finditer(pattern2, lines[i]):
                matches_pattern.append(match.group())
                match_found = True
            for match in re.finditer(pattern5, lines[i]):
                matches_pattern5.append(match.group())
                match_found = True
            for match in re.finditer(pattern6, lines[i]):
                no_num_matches.append(match.group()[:1])
            else:
                for match in re.finditer(pattern1, lines[i]):
                    matches_pattern1.append(match.group())
                    match_found = True
            if match_found == False:
                print(f"error at {articles[k]['title']} ")
                error_type = 'Нарушена пунктуация подпункта/подпункта'
                error = {
                    "error_type": error_type,
                    "error_text": [articles[i]['title'], lines[i]],
                    "start": -1,
                    "end": -1,
                }
                errors.append(error)
                # print(lines[i])
                # print("=====111")

    lines = lines[1:]
    return lines, matches_pattern5, matches_pattern4, matches_pattern, no_num_matches

# Выводит все индексы частей и подпунктов в список


def create_indices(articles, ind):
    pattern3 = re.compile(r'^[^А-Яа-я]+')
    expression = re.compile(r'^[А-Я]+.+\:$')
    pattern = re.compile(r'^[0-9]{1,2}\-{0,1}[0-9]{0,2}[\.\)]{1}')
    lines, matches5, matches4, matches1, no_num_matches = check_seq(
        articles, ind)
    lines = [line for line in lines if pattern3.match(
        line) or expression.match(line)]
    indices = []
    for line in lines:
        match = pattern.match(line)
        match2 = expression.match(line)
        if match:
            indices.append(match.group())
        elif match2:
            indices.append(match2.group()[:9])

    return indices, matches5, matches4, matches1, lines


def is_ordered(lst):
    filtered_lst = [item for item in lst if '-' not in item]
    return filtered_lst == [f"{i})" for i in range(1, len(filtered_lst) + 1)]


def check_numeration_paragraph(indices_dict, key1):
    last_num = 0
    is_special = False

    for i in range(len(indices_dict[key1])):
        try:
            expression = re.compile(r'[0-9]{1,2}\-{0,1}[0-9]{0,2}')
            expression1 = re.compile(r'[0-9]{1}\-{0,1}[0-9]{0,2}')
            expression2 = re.compile(r'[0-9]{2}\-{0,1}[0-9]{0,2}')
            match = re.findall(expression, indices_dict[key1][i][:4])
            match1 = re.findall(expression1, indices_dict[key1][i][:4])
            match2 = re.findall(expression2, indices_dict[key1][i][:4])
            # print(f"current match is {match[0]}")
            # print(f"current indice is {indices_dict[key1][i][:2]}")
            if len(match[0]) > 2:
                if len(match2) > 0:
                    num = int(match[0][:2])
                    is_special = True
                elif len(match1) > 0:
                    num = int(match[0][:1])
                    is_special = True
            else:
                num = int(match[0])
                is_special = False
        except ValueError:
            return False

        # print(last_num) , print(num)
        if is_special:
            if num != last_num:
                print(f"error at paragraph number {num}")
                error_type = 'Нарушена нумерация подпункта'
                error = {
                    "error_type": error_type,
                    "error_text": indices_dict[key1][i],
                    "start": -1,
                    "end": -1,
                }
                errors.append(error)
                return False
        else:
            if num != last_num + 1:
                print(f"error at paragraph number {num}")
                error_type = 'Нарушена нумерация подпункта'
                error = {
                    "error_type": error_type,
                    "error_text": indices_dict[key1][i],
                    "start": -1,
                    "end": -1,
                }
                errors.append(error)
                return False

        last_num = num
        # print(last_num) , print(num)
        # print(indices_dict[key1][i])
        # print("========")

    return True


def check_numeration_punkt(matches_pattern):
    last_num = 0
    is_special = False

    for i in range(len(matches_pattern)):
        try:
            expression = re.compile(r'[0-9]{1,2}\-{0,1}[0-9]{0,2}')
            expression1 = re.compile(r'[0-9]{1}\-{0,1}[0-9]{0,2}')
            expression2 = re.compile(r'[0-9]{2}\-{0,1}[0-9]{0,2}')
            # expression3 = re.compile(r'^[А-Я]')
            match = re.findall(expression, matches_pattern[i][:2])
            match1 = re.findall(expression1, matches_pattern[i][:2])
            match2 = re.findall(expression2, matches_pattern[i][:2])
            # match3 = re.findall(expression2,matches_pattern[i][:2])
            if len(match[0]) > 2:
                if len(match2) > 0:
                    num = int(match[0][:2])
                    is_special = True
                    continue
                elif len(match1) > 0:
                    num = int(match[0][:1])
                    is_special = True
                    continue
            else:
                num = int(match[0])
                is_special = False
        except ValueError:
            return False

        # print(last_num) , print(num)
        if is_special:
            if num != last_num:
                print(f"error at punkt number {num}")
                error_type = 'Нарушена нумерация пункта'
                error = {
                    "error_type": error_type,
                    "error_text": matches_pattern[i],
                    "start": -1,
                    "end": -1,
                }
                errors.append(error)

                return False
        else:
            if num != last_num + 1:
                print(f"error at punkt number {num}")
                error_type = 'Нарушена нумерация пункта'
                error = {
                    "error_type": error_type,
                    "error_text": matches_pattern[i],
                    "start": -1,
                    "end": -1,
                }
                errors.append(error)
                return False

        last_num = num
        # print(last_num) , print(num)
        # print(indices_dict[key1][i])
        # print("========")

    return True


def create_dict(indices):
    indices_dict = {}

    temp_list = []

    current_key = None
    pattern = re.compile(r'^[А-Я]')
    for item in indices:
        if item.endswith('.') or pattern.match(item):
            if current_key is not None:
                indices_dict[current_key] = temp_list
            temp_list = []
            current_key = item
        elif item.endswith(')'):
            temp_list.append(item)

    if current_key is not None and temp_list:
        indices_dict[current_key] = temp_list

    if indices[len(indices)-1].endswith('.'):
        temp_list = []
        indices_dict[indices[len(indices)-1]] = temp_list

    return indices_dict


def create_dict_unique_keys(indices):
    indices_dict = {}
    temp_list = []
    current_key = None
    key_counts = {}
    pattern = re.compile(r'^[А-Я]')

    for item in indices:
        if item.endswith('.') or pattern.match(item):
            if item in key_counts:
                key_counts[item] += 1
            else:
                key_counts[item] = 1

            unique_key = f"{item}_{key_counts[item]}"

            if current_key is not None:
                indices_dict[current_key] = temp_list

            temp_list = []
            current_key = unique_key

        elif item.endswith(')'):
            temp_list.append(item)

    if current_key is not None and temp_list:
        indices_dict[current_key] = temp_list

    # Последний key должен иметь свои items , даже если они пустые
    if indices[-1].endswith('.'):
        temp_list = []
        # проверка на уникальность key
        final_item = indices[-1]
        final_count = key_counts.get(final_item, 0) + 1
        final_unique_key = f"{final_item}_{final_count}"
        indices_dict[final_unique_key] = temp_list

    return indices_dict


def filter_complex_numeration(items):
    complex_numerated_items = []

    for item in items:
        if '-' in item and item.split('-')[1].strip().rstrip(')').isdigit():
            complex_numerated_items.append(item)

    for item in items:
        if '-' in item and item.split('-')[1].strip().rstrip('.').isdigit():
            complex_numerated_items.append(item)

    return complex_numerated_items


def group_by_numeration(items):
    grouped_items = {}
    for item in items:
        main_numeration = item.split('-')[0].strip()
        if main_numeration not in grouped_items:
            grouped_items[main_numeration] = []
        grouped_items[main_numeration].append(item)
    return list(grouped_items.values())


def check_sec_numeration_paragraph(items):
    last_num = 0
    is_special = False

    for i in range(len(items)):
        try:
            expression = re.compile(r'[0-9]{1,2}\-{0,1}[0-9]{0,2}')
            expression1 = re.compile(r'[0-9]{1}\-{0,1}[0-9]{0,2}')
            expression2 = re.compile(r'[0-9]{2}\-{0,1}[0-9]{0,2}')
            match = re.findall(expression, items[i])
            match1 = re.findall(expression1, items[i])
            match2 = re.findall(expression2, items[i])
            if len(match[0]) > 2:
                if len(match2) > 0:
                    num = int(match[0][3:4])
                    is_special = True
                elif len(match1) > 0:
                    num = int(match[0][2:3])
                    is_special = True
            else:
                num = int(match[0])
                is_special = False
        except ValueError:
            return False

        # print(last_num) , print(num)
        if is_special:
            if num != last_num + 1:
                print(f"error at paragraph number {num}")
                error_type = 'Нарушена нумерация сложно-нумерированных подпунктов'
                error = {
                    "error_type": error_type,
                    "error_text": items[i],
                    "start": -1,
                    "end": -1,
                }
                errors.append(error)
                return False
        else:
            if num != last_num + 1:
                print(f"error at paragraph number {num}")
                error_type = 'Нарушена нумерация сложно-нумерированных подпунктов'
                error = {
                    "error_type": error_type,
                    "error_text": items[i],
                    "start": -1,
                    "end": -1,
                }
                errors.append(error)
                return False

        last_num = num
        # print(last_num) , print(num)
        # print(items[i])
        # print("========")

    return True


def main_check(articles):
    for i in range(len(articles)):
        try:
            print(articles[i]['title'])
            indices, matches5, matches4, matches1, lines = create_indices(
                articles, i)

            if len(indices) == 0:
                continue

            indices_dict = create_dict_unique_keys(indices)

            if len(matches1) > 0:
                check_numeration_punkt(matches1)

            grouped_num_items = group_by_numeration(matches4)
            for item in grouped_num_items:
                is_ordered1 = check_sec_numeration_paragraph(item)
                if not is_ordered1:
                    # print("Ошибка в двойной нумерации пунктов")
                    break

            if len(indices_dict) == 0:
                is_ordered_result = is_ordered(indices)
                if not is_ordered_result:
                    # print("Ошибка в нумерации подпунктов")
                    error_type = 'Нарушена нумерация подпункта'
                    error = {
                        "error_type": error_type,
                        "error_text": [articles[i]['title'], indices],
                        "start": -1,
                        "end": -1,
                    }
                    errors.append(error)

                    grouped_num_items = group_by_numeration(matches5)
                    for item in grouped_num_items:
                        is_correct = check_sec_numeration_paragraph(item)
                        if not is_correct:
                            # print("Ошибка в двойной нумерации подпунктов")
                            break

            else:
                for key, values in indices_dict.items():
                    if values is not None:
                        complex_numerated_items = filter_complex_numeration(
                            indices_dict[key])
                        if len(complex_numerated_items) > 0:
                            grouped_num_items = group_by_numeration(
                                complex_numerated_items)
                            for item in grouped_num_items:
                                if not check_sec_numeration_paragraph(item):
                                    # print("Ошибка в нумерации подпунктов")
                                    break

                    is_correct = check_numeration_paragraph(indices_dict, key)
                    if not is_correct:
                        # print("Ошибка в нумерации подпунктов")
                        break

        except Exception as e:
            # print(f"Unexpected error occurred: {e}")
            tb_str = traceback.format_exc()
            exception_errors.append(
                f"{articles[i]['title']} : Unexpected error: {e} in article {i}\nTraceback: {tb_str}")


if __name__ == '__main__':
    errors = []
    exception_errors = []
    docx_file = "../data/docx/Налоговый кодекс.docx"
    text = extract_text_from_docx(docx_file)
    cleaned_text = remove_footnotes(text)
    chapters, articles = segment_pdf_text_across_pages(cleaned_text)
    is_correct = check_numeration_chapter(chapters)
    # print(f"Numeration of chapters is correct: {is_correct}")
    is_correct = check_numeration_article(articles)
    # print(f"Numeration of articles is correct: {is_correct}")
    is_correct = check_chapter_punctuation(chapters)
    # print(f"Punctuation of chapters is correct: {is_correct}")
    is_correct = check_article_punctuation(articles)
    # print(f"Punctuation of articles is correct: {is_correct}")

    main_check(articles)
    print(errors)

    print("-----------------")
    print(exception_errors)
    # with open("errors1.txt", "w", encoding='utf-8') as error_file:
    #     for error in errors:
    #         error_file.write(json.dumps(error, ensure_ascii=False, indent=4))
    #         error_file.write("=====\n")
    #         error_file.write("=====\n")
