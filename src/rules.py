import re
import traceback

errors = []
exception_errors = []
cleaned_text = ''


def segment_pdf_text_across_pages(full_text):
    chapter_pattern = re.compile(
        r'(Глава\s*\d+\s*\..*?)(?=Глава\s*\d+\s*\.|$)', re.DOTALL)
    # adding \s to the article pattern
    article_pattern = re.compile(
        r'(Статья\s*\d+(?:-\d+)?\s*\..*?)(?=Статья\s*\d+(?:-\d+)?\s*\.|$)', re.DOTALL)

    chapters = [{'title': m.group(1).split('\n', 1)[0], 'content': m.group(
        1)} for m in chapter_pattern.finditer(full_text)]
    articles = [{'title': m.group(1).split('\n', 1)[0], 'content': m.group(
        1)} for m in article_pattern.finditer(full_text)]

    return chapters, articles


def search_pattern_from_start(text, start):
    pattern = re.compile(
        r'[\s\t\n]+[1-9]{1}[0-9]{1}\-{0,1}[0-9]{0,2}\.{1}[\s]+|\n[А-Я] |Статья\s\d+')
    if start >= len(text):
        return -1
    match = re.search(pattern, text[start:])
    if match:
        return match.start() + start
    else:
        return -1


def find_violation_position(text, target, whole_text):
    pattern = r'\d+\) [^;]+'
    strings = re.findall(pattern, text)
    prev_num = 0
    for s in strings:
        num = int(s.split(')')[0])
        if num == target and (num != prev_num + 1 and prev_num != 0):
            position = whole_text.find(s)
            return position
        prev_num = num
    return None


def check_ending_punctuation(articles, key):
    # removed '\n', before '\n' + str(articles[key]['title'])
    start_sub_index = cleaned_text.find(str(articles[key]['title']))
    # removed '\n', before '\n' + str(articles[key]['title'])
    end_sub_index = cleaned_text.find(str(articles[key+1]['title']))
    new_text = cleaned_text[start_sub_index-2: end_sub_index]
    strings = re.split(r'\n\n|(?<=;)', new_text)
    # strings = strings [1:len(strings)-1]
    strings = [s.strip() for s in strings]
    strings = [string for string in strings if string is not None]
    strings = [s for s in strings if 'Статья' not in s]
    strings = [s for s in strings if s != '\xa0\xa0\xa0\xa0\xa0 ']
    strings = [s for s in strings if s]
    strings = [s.strip() for s in strings]

    # добавить латинские буквы в паттерн(возможно)
    pattern = re.compile(r'[А-Яа-я]')
    pattern1 = re.compile(r'[А-Я]')
    pattern2 = re.compile(r'[а-я]')
    pattern3 = re.compile(r'(?=.*\d)(?=.*[A-ZА-ЯЁ])[A-ZА-ЯЁ\d]+')

    for i, string in enumerate(strings):
        match = re.search(pattern, string)
        words = re.findall(r'\b\w+\b', string)
        codematch = re.findall(pattern3, words[0])
        if len(codematch) > 0:
            continue
        if match is None:
            continue

        if i == 0 or strings[i-1][-1] in ('.', '!', '?'):
            match2 = re.findall(pattern1, match.group())
            if not match2:
                error_type = 'Нарушение в начале абзаца. Абзац должен начинаться с заглавной буквы'
                a = cleaned_text.find(strings[i], start_sub_index)
                b = a + 1
                error = {
                    "error_type": error_type,
                    "error_text": [articles[key]['title'], strings[i]],
                    "start": a,
                    "end": b
                }
                errors.append(error)

        if strings[i-1][-1] in (':', ';'):
            match3 = re.findall(pattern2, match.group())
            if not match3:
                error_type = 'Нарушение в начале абзаца. Абзац должен начинаться со строчной буквы'
                a = cleaned_text.find(strings[i], start_sub_index)
                b = a + 1
                error = {
                    "error_type": error_type,
                    "error_text": [articles[key]['title'], strings[i]],
                    "start": a,
                    "end": b
                }
                errors.append(error)

# def check_ending_punctuation(articles, key):
#     # Handle edge cases for article indexing
#     if key >= len(articles) - 1:
#         return  # Exit function if key is out of bounds for articles

#     # Safely extract titles and their positions in the cleaned text
#     start_sub_index = max(0, cleaned_text.find(articles[key]['title']))
#     end_sub_index = cleaned_text.find(
#         articles[key + 1]['title'], start_sub_index)
#     if end_sub_index == -1:
#         end_sub_index = len(cleaned_text)

#     new_text = cleaned_text[start_sub_index: end_sub_index]
#     strings = re.split(r'\n\n|(?<=;)', new_text)
#     strings = [s.strip() for s in strings if s.strip()
#                and 'Статья' not in s and s != '\xa0\xa0\xa0\xa0\xa0 ']

#     # Patterns for checking capitalization
#     pattern_capital = re.compile(r'[А-Я]')
#     pattern_non_capital = re.compile(r'[а-я]')

#     # Pattern to exclude codes and abbreviations
#     pattern_code = re.compile(r'(?=.*\d)(?=.*[A-ZА-ЯЁ])[A-ZА-ЯЁ\d]+')

#     for i, string in enumerate(strings):
#         if not string or pattern_code.findall(string.split()[0]):
#             continue  # Skip empty strings or strings starting with a code

#         # Check for starting capital or non-capital letter as per punctuation rules
#         start_letter = string[0]
#         prev_char = strings[i-1][-1] if i > 0 else None

#         # Determine error type based on preceding character and capitalization
#         if prev_char in ('.', '!', '?') and not pattern_capital.match(start_letter):
#             error_type = 'Нарушение в начале абзаца. Абзац должен начинаться с заглавной буквы'
#         elif prev_char in (':', ';') and not pattern_non_capital.match(start_letter):
#             error_type = 'Нарушение в начале абзаца. Абзац должен начинаться со строчной буквы'
#         else:
#             continue  # No error found

#         # Record the error
#         error_position = cleaned_text.find(string, start_sub_index)
#         errors.append({
#             "error_type": error_type,
#             "error_text": [articles[key]['title'], string],
#             "start": error_position,
#             "end": error_position + 1
#         })


def find_violation_position1(text, target, whole_text):
    pattern = re.compile(r'(?<!-)[0-9]{1,3}\..+[\:\.]')
    strings = re.findall(pattern, text)
    prev_num = 0
    for s in strings:
        # print(s)
        num = int(s.split('.')[0])
        if num == target and (num != prev_num + 1 and prev_num != 0):
            position = whole_text.find(s)
            return position
        prev_num = num
    return None


def create_indices1(articles, ind):
    expression = re.compile(r'^[А-Яа-я\s]+')
    pattern = re.compile(r'^[0-9]{1,2}\-{0,1}[0-9]{0,2}[\.\)]{1}')
    pre_lines = articles[ind]['content'].split('\n')
    lines = [line.strip() for line in pre_lines if line.strip()]
    lines = lines[1:]
    indices = []
    for line in lines:
        match = pattern.match(line)
        match2 = expression.match(line)
        if match:
            indices.append(match.group())
        elif match2:
            indices.append(match2.group()[:9])

    return indices, lines

# Проверка на отсутствие слова Часть перед номером части


def check_punkt_punctuation(lines, articles, i):
    pattern = re.compile(r'^(Часть|часть|част).{0,5}[0-9]{1,2}[/./)]{0,1}')
    for line in lines:
        match1 = re.match(pattern, line)
        if match1:
            a1 = cleaned_text.find(articles[i]['title'])
            a = cleaned_text.find(match1.group(), a1)
            b = a + 3
            error_type = "Нарушение названия части :Название части не должно содержать само слово 'Часть' "
            error = {
                "error_type": error_type,
                "error_text": f"{articles[i]['title']}  нарушение пунктуации , найдены лишние слова  {line} ",
                "start": a,
                "end": b,
            }
            errors.append(error)

# Ошибка в нахождении римских цифр


def check_roman_numbers(cleaned_text):
    # changed pattern to match only the roman numbers that resemble часть or подпункт in the beginning of the line pattern_roman = re.compile(r'(X{0,3})(IX|IV|V?I{0,3})(ix|iv|v?i{0,3})')
    pattern_roman = re.compile(r'\n\s*(X|x) |\n\s*(V|v)|\n\s*(I|i)')
    matches = pattern_roman.finditer(cleaned_text)
    for match in matches:
        if len(match.group()) > 0:
            error_type = 'Найдена римская нумерация'
            # a1 = cleaned_text.find(articles[i]['title'])
            # a = cleaned_text.find(match.group(), a1)
            # b = a + 3
            error = {
                "error_type": error_type,
                "error_text": match.group(),
                "start": match.start(),
                "end": match.end(),
            }
            errors.append(error)


def is_ordered(lst, is_chapter=False, articles=None, k=None, key=None):
    pattern = re.compile(r'^[0-9]+')
    filtered_lst = [int(pattern.match(item).group())
                    for item in lst if '-' not in item]

    def generate_error_message(i, numbers):
        if key is None and k is not None:
            error_type = "Нарушена нумерация части"
            error_text = f"{articles[k]['title']} в части {numbers[i]}"
            start_sub_index = cleaned_text.find('\n'+str(articles[k]['title']))
            end_sub_index = cleaned_text.find('\n'+str(articles[k+1]['title']))
            new_text = cleaned_text[start_sub_index-2: end_sub_index]
            a = find_violation_position1(new_text, numbers[i], cleaned_text)
            b = a + 3
        elif key is not None and k is not None:
            error_type = "Нарушена нумерация подпункта"
            error_text = f"{articles[k]['title']} в части {key} и пункте {numbers[i]}"
            spec_pattern = r'[0-9]{1,3}-{1}[0-9]{1,2}\.{1}'
            match = re.findall(spec_pattern, key)
            if len(match) > 0:
                rkey = match[0]
            elif len(key) == 4:
                rkey = key[:2]
            elif len(key) == 5:
                rkey = key[:3]
            else:
                rkey = key[:5]
            index = cleaned_text.find('\n'+str(articles[k]['title']))
            if k == 0:
                start_sub_index = cleaned_text.find(rkey, index+9)
            else:
                start_sub_index = cleaned_text.find(rkey, index+4)
            end_sub_index = search_pattern_from_start(
                cleaned_text, start_sub_index + 10)
            new_text = cleaned_text[start_sub_index-2: end_sub_index]
            a = find_violation_position(new_text, numbers[i], cleaned_text)
            b = a + 3
        elif not is_chapter and key is None and k is None:
            error_type = 'Нумерация статей нарушена'
            a = cleaned_text.find('\nСтатья '+str(numbers[i]))
            b = a + 12
            error_text = cleaned_text[a:b]
        else:
            error_type = 'Unknown error'
            error_text = 'An unknown error has occurred'

        return {
            "error_type": error_type,
            "error_text": error_text,
            "start": a,
            "end": b,
        }

    for i in range(1, len(filtered_lst)):
        if filtered_lst[i-1] + 1 != filtered_lst[i]:
            error = generate_error_message(i, filtered_lst)
            errors.append(error)


# проверка пунктуации глав
def check_chapter_punctuation(chapters):
    pattern = re.compile(r"^Глава\s[0-9]{1,2}\.\s.*")
    error_type = ''
    for i in range(len(chapters)):
        match = re.match(pattern, chapters[i]['title'])
        if not match:
            a = cleaned_text.find(chapters[i]['title'])
            b = a + 8
            error_type = 'Пунктуация названия глав нарушена'
            error = {
                "error_type": error_type,
                "error_text": chapters[i]['title'],
                "start": a,
                "end": b,
            }
            errors.append(error)


# Проверка пунктуации статей
def check_article_punctuation(articles):
    pattern = re.compile(r"^Статья\s[0-9]{1,3}\-{0,1}[0-9]{0,2}\.\s.*")
    # pattern1 = re.compile(r"[0-9]{1,3}\-{0,1}[0-9]{0,2}+")
    pattern1 = re.compile(r"[0-9]{1,3}-?[0-9]{0,2}")
    article_nums = []
    for i in range(len(articles)):
        match = re.findall(pattern, articles[i]['title'])
        match1 = re.findall(pattern1, articles[i]['title'])
        if len(match1) > 0:
            article_nums.append(match1)
        if len(match) == 0:
            a = cleaned_text.find(articles[i]['title'])
            b = a + 8
            error_type = 'Пунктуация названия статей нарушена'
            error = {
                "error_type": error_type,
                "error_text": articles[i]['title'],
                "start": a,
                "end": b,
            }
            errors.append(error)

    flattened_list = [item for sublist in article_nums for item in sublist]
    simple_numbers = []
    complex_numbers = []

    for item in flattened_list:
        if '-' in item:
            complex_numbers.append(item)
        else:
            simple_numbers.append(item)

    grouped_num_items = group_by_numeration(complex_numbers)
    for item in grouped_num_items:
        check_sec_numeration_paragraph(item)

    is_ordered(simple_numbers, False, articles, None, None)


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
                a = cleaned_text.find(chapters[i]['title'])
                b = a + 8
                error_type = 'Нарушена нумерация глав'
                error = {
                    "error_type": error_type,
                    "error_text": chapters[i]['title'],
                    "start": a,
                    "end": b,
                }
                errors.append(error)
        else:
            if num != last_num + 1:
                a = cleaned_text.find(chapters[i]['title'])
                b = a + 8
                error_type = 'Нарушена нумерация глав'
                error = {
                    "error_type": error_type,
                    "error_text": chapters[i]['title'],
                    "start": a,
                    "end": b,
                }
                errors.append(error)
        last_num = num
        # print("========")


# Проверка на пунктуацию пунктов/подпунктов

def check_seq(articles, k):
    pre_lines = articles[k]['content'].split('\n')

    lines = [line.strip() for line in pre_lines if line.strip()]

    pattern = re.compile(r'^[0-9]')
    pattern1 = re.compile(r'^[0-9]+\)\s{1}')
    pattern2 = re.compile(r'^[0-9]+\.\s')
    pattern3 = re.compile(r'^[А-Яа-я]+')
    pattern4 = re.compile(r'^[0-9]{1,3}\-{1}[0-9]{1,2}\.\s')
    pattern5 = re.compile(r'^[0-9]{1,3}\-{1}[0-9]{1,2}\)')
    # this pattern was created for ignoring the lines that start with latin characters
    pattern6 = re.compile(r'^[A-Za-z]+')

    matches_pattern = []
    matches_pattern1 = []
    matches_pattern5 = []
    matches_pattern4 = []

    first_line_matches = list(re.finditer(pattern, lines[1]))

    if len(first_line_matches) > 0:
        for i in range(1, len(lines)):
            match_found = False
            for match in re.finditer(pattern3, lines[i]):
                if len(match.group()) > 0:
                    match_found = True
                    continue
            for match in re.finditer(pattern6, lines[i]):
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
            else:
                for match in re.finditer(pattern1, lines[i]):
                    matches_pattern1.append(match.group())
                    match_found = True

            if match_found == False:
                a_ind = cleaned_text.find(articles[k]['title'])
                a = cleaned_text.find(lines[i], a_ind)
                b = a + 8
                error_type = 'Нарушена пунктуация пункта/подпункта'
                error = {
                    "error_type": error_type,
                    "error_text": [articles[k]['title'], lines[i]],
                    "start": a,
                    "end": b,
                }
                errors.append(error)
                # print(lines[i])
                # print("========")
    else:
        for i in range(2, len(lines)):
            match_found = False
            for match in re.finditer(pattern3, lines[i]):
                if len(match.group()) > 0:
                    match_found = True
                    continue
            for match in re.finditer(pattern6, lines[i]):
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
            else:
                for match in re.finditer(pattern1, lines[i]):
                    matches_pattern1.append(match.group())
                    match_found = True
            if match_found == False:
                a_ind = cleaned_text.find(articles[k]['title'])
                a = cleaned_text.find(lines[i], a_ind)
                b = a + 8
                error_type = 'Нарушена пунктуация пункта/подпункта'
                error = {
                    "error_type": error_type,
                    "error_text": [articles[i]['title'], lines[i]],
                    "start": a,
                    "end": b,
                }
                errors.append(error)
                # print(lines[i])
                # print("=========")

    lines = lines[1:]
    return lines, matches_pattern5, matches_pattern4, matches_pattern, matches_pattern1


# Выводит все индексы частей и подпунктов в список
def create_indices(articles, ind):
    pattern3 = re.compile(r'^[^А-Яа-я]+')
    expression = re.compile(r'^[А-Яа-я]+.+\:$')
    pattern = re.compile(r'^[0-9]{1,3}\-{0,1}[0-9]{0,2}[\.\)]{1}')
    lines, matches5, matches4, matches1, matches_pattern1 = check_seq(
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

    return indices, matches5, matches4, matches1, lines, matches_pattern1


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
    pattern = re.compile(r'^[А-Яа-я]')

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


def check_sec_numeration_paragraph(items, articles=None, k=None, key=None):
    last_num = 0
    is_special = False
    for i in range(len(items)):
        try:
            expression = re.compile(r'^[0-9]{1,3}\-{0,1}[0-9]{0,2}')
            expression1 = re.compile(r'^[0-9]{1}\-{1}[0-9]{1,2}')
            expression2 = re.compile(r'^[0-9]{2}\-{1}[0-9]{1,2}')
            expression3 = re.compile(r'^[0-9]{3}\-{1}[0-9]{1,2}')
            expression4 = re.compile(r'^[0-9]{2}\-{1}[0-9]{2}')
            expression5 = re.compile(r'^[0-9]{1}\-{1}[0-9]{2}')
            match = re.findall(expression, items[i])
            match1 = re.findall(expression1, items[i])
            match2 = re.findall(expression2, items[i])
            match3 = re.findall(expression3, items[i])
            match4 = re.findall(expression4, items[i])
            match5 = re.findall(expression5, items[i])
            if len(match[0]) > 2:
                if len(match5) > 0:
                    num = int(match[0][2:4])
                    is_special = True
                elif len(match4) > 0:
                    num = int(match[0][3:5])
                    is_special = True
                elif len(match2) > 0:
                    num = int(match[0][3:4])
                    is_special = True
                elif len(match1) > 0:
                    num = int(match[0][2:3])
                    is_special = True
                elif len(match3) > 0:
                    num = int(match[0][4:5])
                    is_special = True
            else:
                num = int(match[0])
                is_special = False

        # print(last_num) , print(num)
            if is_special:
                if num != last_num + 1:
                    error_type = 'Нарушена нумерация сложно-нумерированных статей'
                    if articles == None:
                        a = cleaned_text.find('\nСтатья '+str(items[i]))
                        b = a + 12
                        error = {
                            "error_type": error_type,
                            "error_text": f" ошибка в  Статье {items[i]}",
                            "start": a,
                            "end": b,
                        }
                        errors.append(error)
                    elif key == None:
                        index = cleaned_text.find(articles[k]['title'])
                        a = cleaned_text.find(items[i], index)
                        b = a + 6
                        error_type = 'Нарушена нумерация сложно-нумерированных частей/подпунктов'
                        error = {
                            "error_type": error_type,
                            "error_text": f" {articles[k]['title']} в части {key} и подпункте {items[i]}",
                            "start": a,
                            "end": b,
                        }
                        errors.append(error)

                    else:
                        index = cleaned_text.find(articles[k]['title'])
                        key = key.split('_')[0]
                        sub_index = cleaned_text.find(key, index)
                        a = cleaned_text.find(items[i], sub_index)
                        b = a + 6
                        error_type = 'Нарушена нумерация сложно-нумерированных частей/подпунктов'
                        error = {
                            "error_type": error_type,
                            "error_text": f" {articles[k]['title']} в части {key} и подпункте {items[i]}",
                            "start": a,
                            "end": b,
                        }
                        errors.append(error)

            else:
                if num != last_num + 1:
                    error_type = 'Нарушена нумерация сложно-нумерированных подпунктов'
                    error = {
                        "error_type": error_type,
                        "error_text": items[i],
                        "start": -1,
                        "end": -1,
                    }
                    errors.append(error)

            last_num = num
            # print(last_num) , print(num)
            # print(items[i])
            # print("========")
        except ValueError:
            print('Error occurred in numeration check' + str(match[0]))
            return False


def main_check(articles):
    for i in range(len(articles)):
        try:
            indices, matches5, matches4, matches3, lines, matches1 = create_indices(
                articles, i)
            # print(f"LENGTH OF INDICES  {len(indices)}")
            if len(indices) == 0:
                # print('non')
                continue
            else:
                indices_dict = create_dict_unique_keys(indices)
            if len(matches3) > 0:
                is_ordered(matches3, None,  articles, i, None)
            # print(indices_dict)
            grouped_num_items = group_by_numeration(matches4)
            for item in grouped_num_items:
                check_sec_numeration_paragraph(item, articles, i)

            if len(indices_dict) == 0:
                grouped_num_items = group_by_numeration(matches5)
                for item in grouped_num_items:
                    check_sec_numeration_paragraph(item, articles, i)

            else:
                for key, values in indices_dict.items():
                    if values is not None:
                        is_ordered(indices_dict[key], False, articles, i, key)
                        complex_numerated_items = filter_complex_numeration(
                            indices_dict[key])
                        if len(complex_numerated_items) > 0:
                            grouped_num_items = group_by_numeration(
                                complex_numerated_items)
                            for item in grouped_num_items:
                                check_sec_numeration_paragraph(
                                    item, articles, i, key)

                check_ending_punctuation(articles, i)

            # len(complex_numerated_items)
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            tb_str = traceback.format_exc()
            exception_errors.append(
                f"{articles[i]['title']} : Unexpected error: {e} in article {i}\nTraceback: {tb_str}")
            continue


def check_main_rules(full_text):
    global cleaned_text
    global errors
    global exception_errors
    errors = []
    exception_errors = []
    cleaned_text = full_text
    chapters, articles = segment_pdf_text_across_pages(cleaned_text)
    check_numeration_chapter(chapters)
    check_chapter_punctuation(chapters)
    check_article_punctuation(articles)
    main_check(articles)
    # print(cleaned_text[126817:126837])
    check_roman_numbers(cleaned_text)
    for i in range(len(articles)):
        indices1, lines1 = create_indices1(articles, i)
        check_punkt_punctuation(lines1, articles, i)

    return errors
    # print(errors)
    # print('=====================')
    # print(len(errors))
    # print('=====================')
    # print(exception_errors)
    # with open("errors1.txt", "w", encoding='utf-8') as error_file:
    #     for error in errors:
    #         error_file.write(json.dumps(error, ensure_ascii=False, indent=4))
    #         error_file.write("=====\n")
    #         error_file.write("=====\n")
