import re
from typing import List
import streamlit as st
from llama_index.bridge.pydantic import BaseModel, Field
from llama_index.llms import OpenAI
from llama_index.program import OpenAIPydanticProgram
import pandas as pd
import streamlit_shadcn_ui as ui

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]


class SyntaxCheck(BaseModel):
    """Data model for syntax and text formatting check."""

    user_input: str = Field(..., description="The user_input.")
    valid: bool = Field(
        ..., description="True if user_input pass the criteria, else False."
    )
    error_highlight: str = Field(
        ..., description="The exact user input that fails to meet the criteria."
    )
    error_desc: List[str] = Field(
        ..., description="The concise description of the error in Russian language."
    )


def title_check(user_input: str) -> SyntaxCheck:
    """Check user_input for Title rule from law tech.

    Args:
        user_input (str): Legal document to check.

    """
    prompt_str = """
    Instructions:

    You are an AI language model capable of analyzing and evaluating legal documents according to the following text formatting and syntax rule:

    The title (Title) of the normative legal act must indicate the subject of regulation of the adopted normative legal act and must be brief.
    Your task is to analyze the input legal document and check if the title meets the specified criteria. If the title does not meet the criteria, please highlight it in the text and provide a brief explanation of the error. If the title meets the criteria, please indicate that the title is error-free.
    With the following JSON format.

    Input: {user_input}

    Output: """

    program = OpenAIPydanticProgram.from_defaults(
        output_cls=SyntaxCheck,
        llm=OpenAI(api_key=OPENAI_API_KEY, model="gpt-4-0125-preview"),
        prompt_template_str=prompt_str,
        verbose=True,
    )

    return program(user_input=user_input)


def remove_footnotes(text):
    # Регулярное выражение для поиска абзацев, начинающихся с "Сноска." и заканчивающихся точкой с пробелом,
    # за исключением случаев с сокращениями типа "см."
    pattern = r"Сноска\..*?(?<!см)\.\s"
    cleaned_text = re.sub(pattern, "", text, flags=re.DOTALL)
    return cleaned_text


# Модифицированная функция для проверки корректности дат
def check_date_format(date):
    # Добавлено условие для распознавания дат в формате DD.MM.YYYY
    correct_format = re.compile(
        r"(\b\d{1,2}\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s\d{4}\sгода\b)|(\b\d{1,2}[.]\d{1,2}[.]\d{4}\b)"
    )
    return bool(correct_format.match(date))


def find_incorrect_dates(text):
    incorrect_dates = []
    # Измененное регулярное выражение для поиска всех возможных дат
    date_pattern = re.compile(
        r"\b\d{1,2}[\s.-](января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря|\d{1,2})[\s.-]\d{2,4}(?:\sгода)?\b"
    )
    for match in date_pattern.finditer(text):
        date = match.group(0)
        # Проверяем дату на соответствие одному из корректных форматов
        if not check_date_format(date):
            incorrect_dates.append(
                {
                    "error_type": "Некорректный формат даты",
                    "error_text": date,
                    "start": match.start(),
                    "end": match.end(),
                }
            )
    return incorrect_dates

# Функция для проверки нумерации


def normalize_article_number(match):
    # Разделяем номер статьи и подпункт, если он есть
    parts = match.split('-')
    if len(parts) == 1:
        # Если подпункта нет, возвращаем основной номер и 0 в качестве подпункта
        return int(parts[0]), 0
    else:
        # Возвращаем основной номер и номер подпункта
        return int(parts[0]), int(parts[1])


def compare_article_numbers(prev, current):
    # Сравниваем основные номера и номера подпунктов
    if current[0] == prev[0]:
        return current[1] == prev[1] + 1
    else:
        return current[0] == prev[0] + 1 and current[1] == 0


def check_article_numbering(text):
    pattern = r"Статья (\d+(?:-\d+)?)"
    matches = list(re.finditer(pattern, text))
    issues = []
    for i in range(1, len(matches)):
        current_number = normalize_article_number(matches[i].group(1))
        previous_number = normalize_article_number(matches[i - 1].group(1))

        if not compare_article_numbers(previous_number, current_number):
            issue_text = f"Статья {matches[i-1].group(1)} и Статья {matches[i].group(1)}"
            issues.append({
                "error_type": "Нарушение нумерации статей",
                "error_text": issue_text,
                "start": matches[i].start(),
                "end": matches[i].end(),
            })
    return issues

# Функция для проверки начала абзацев


def check_paragraphs_start(text):
    pattern = r"(?<=\n)\s*[а-я]"
    issues = []
    context_length = 30  # Количество символов для отображения до и после найденной позиции

    for match in re.finditer(pattern, text):
        start = max(match.start() - context_length, 0)
        end = min(match.end() + context_length, len(text))
        # Заменяем переносы строк на пробелы для удобства чтения
        context = text[start:end].replace("\n", " ")
        issues.append({
            "error_type": "Абзац начинается со строчной буквы",
            "error_text": f"...{context}...",
            "start": match.start(),
            "end": match.end(),
        })
    return issues

# Функция для проверки заголовка


def check_headers(text):
    patterns = {
        "раздел": r"Раздел \d+",
        "подраздел": r"Подраздел \d+",
        "параграф": r"Параграф \d+",
    }
    issues = []
    last_end = 0  # Последняя позиция, где был найден заголовок
    for header, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            issues.append({
                "error_type": "Отсутствует заголовок или подзаголовок",
                "error_text": f"Отсутствует {header}",
                "start": last_end,  # Используем конец последнего найденного заголовка
                # Предполагаем, что ошибка начинается сразу после последнего заголовка
                "end": last_end + 1,
            })
        else:
            last_end = match.end()  # Обновляем последнюю позицию

    return issues

# Функция для выделения ошибок в тексте


def highlight_errors(text, errors):
    # Sort errors by their start position to handle them in order
    errors.sort(key=lambda x: x["start"])

    last_idx = 0  # Keep track of the last index processed
    parts = []  # Collect parts to be passed to annotated_text

    for error in errors:
        # Add text before the error, if any
        if error["start"] > last_idx:
            parts.append(text[last_idx: error["start"]])

        # Extract the error text and add it with annotation
        error_text = text[error["start"]: error["end"]]
        # Use a fixed color, can be customized
        parts.append((error_text, error["error_type"], "#fea"))

        last_idx = error["end"]

    # Add any remaining text after the last error
    if last_idx < len(text):
        parts.append(text[last_idx:])

    # Call annotated_text with the collected parts
    return parts


# Функция для отображения ошибок в Streamlit


def display_errors_with_streamlit(errors):
    # Считаем общее количество ошибок
    total_errors = len(errors)
    # Считаем количество ошибок каждого типа
    if total_errors > 0:
        error_types_count = {}
        for error in errors:
            if error["error_type"] in error_types_count:
                error_types_count[error["error_type"]] += 1
            else:
                error_types_count[error["error_type"]] = 1

        # Выводим общее количество ошибок
        # st.metric(label="Общее количество ошибок", value=total_errors)
        cols = st.columns(5)
        with cols[0]:
            ui.metric_card(title="Общее количество ошибок",
                           content=total_errors, description="", key="card1")

        # Преобразование списка ошибок в DataFrame
        df_errors = pd.DataFrame(errors)
        df_errors.rename(
            columns={"error_type": "Тип ошибки", "error_text": "Текст ошибки"}, inplace=True
        )
        # Вывод таблицы ошибок в Streamlit
        if len(df_errors) > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.write("Детали ошибок:")
                st.table(df_errors[["Тип ошибки", "Текст ошибки"]])
            with col2:
                # Преобразование подсчетов в DataFrame
                st.write("Количество ошибок каждого типа:")
                df_errors = pd.DataFrame(list(error_types_count.items()), columns=[
                    'Тип ошибки', 'Count'])

                # Сортировка для лучшей визуализации (опционально)
                df_errors = df_errors.sort_values(by='Count', ascending=True)

                # Отображение гистограммы в Streamlit
                st.bar_chart(df_errors.set_index('Тип ошибки'), color="#fea")
        # Выводим ошибки красивым образом
        # st.write("Детали ошибок:")
        # for error in errors:
        #     st.error(
        #         f"Тип ошибки: {error['error_type']}" + ' \n ' + f"Текст ошибки: {error['error_text']}")
    else:
        st.success("Ошибок не найдено")

# Функция для отображения результата проверки заголовка в Streamlit


def display_title_check_res(title_check_res):
    st.subheader("Проверка заголовка:")
    if title_check_res.error_highlight != "":
        st.write("Заголовок: ")
        st.subheader(title_check_res.error_highlight)
    if title_check_res.valid == False:
        st.error("Заголовок не соответствует требованиям")
        st.write("Текст ошибки:")
        for error in title_check_res.error_desc:
            st.write("- " + error)
    else:
        st.success("Заголовок соответствует требованиям")
