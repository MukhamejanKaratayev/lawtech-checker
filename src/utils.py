import re


def remove_footnotes(text):
    # Регулярное выражение для поиска абзацев, начинающихся с "Сноска." и заканчивающихся точкой с пробелом,
    # за исключением случаев с сокращениями типа "см."
    pattern = r'Сноска\..*?(?<!см)\.\s'
    # Замена найденных совпадений на пустую строку, используем re.DOTALL для многострочного поиска
    cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)
    return cleaned_text


# Модифицированная функция для проверки корректности дат
def check_date_format(date):
    # Добавлено условие для распознавания дат в формате DD.MM.YYYY
    correct_format = re.compile(
        r'(\b\d{1,2}\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s\d{4}\sгода\b)|(\b\d{1,2}[.]\d{1,2}[.]\d{4}\b)')
    return bool(correct_format.match(date))


def find_incorrect_dates(text):
    incorrect_dates = []
    # Измененное регулярное выражение для поиска всех возможных дат
    date_pattern = re.compile(
        r'\b\d{1,2}[\s.-](января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря|\d{1,2})[\s.-]\d{2,4}(?:\sгода)?\b')
    for match in date_pattern.finditer(text):
        date = match.group(0)
        # Проверяем дату на соответствие одному из корректных форматов
        if not check_date_format(date):
            incorrect_dates.append(
                {"date": date, "start": match.start(), "end": match.end()})
    return incorrect_dates
