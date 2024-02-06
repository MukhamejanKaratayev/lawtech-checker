import re


def remove_footnotes(text):
    # Регулярное выражение для поиска абзацев, начинающихся с "Сноска." и заканчивающихся точкой с пробелом,
    # за исключением случаев с сокращениями типа "см."
    pattern = r'Сноска\..*?(?<!см)\.\s'
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
                {"error_type": 'incorrect date', "error_text": date, "start": match.start(), "end": match.end()})
    return incorrect_dates


def highlight_errors(text, errors):
    # Sort errors by their start position to handle them in order
    errors.sort(key=lambda x: x['start'])

    last_idx = 0  # Keep track of the last index processed
    parts = []  # Collect parts to be passed to annotated_text

    for error in errors:
        # Add text before the error, if any
        if error['start'] > last_idx:
            parts.append(text[last_idx:error['start']])

        # Extract the error text and add it with annotation
        error_text = text[error['start']:error['end']]
        # Use a fixed color, can be customized
        parts.append((error_text, error['error_type'], "#fea"))

        last_idx = error['end']

    # Add any remaining text after the last error
    if last_idx < len(text):
        parts.append(text[last_idx:])

    # Call annotated_text with the collected parts
    return parts
