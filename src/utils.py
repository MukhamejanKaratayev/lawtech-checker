import re
from typing import List
import streamlit as st
from llama_index.bridge.pydantic import BaseModel, Field
from llama_index.llms import OpenAI
from llama_index.program import OpenAIPydanticProgram
import pandas as pd

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
        ..., description="The concise description of the error."
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
                    "error_type": "incorrect date",
                    "error_text": date,
                    "start": match.start(),
                    "end": match.end(),
                }
            )
    return incorrect_dates


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


def display_errors_with_streamlit(errors):
    # Считаем общее количество ошибок
    total_errors = len(errors)
    # Считаем количество ошибок каждого типа
    error_types_count = {}
    for error in errors:
        if error["error_type"] in error_types_count:
            error_types_count[error["error_type"]] += 1
        else:
            error_types_count[error["error_type"]] = 1

    # Выводим общее количество ошибок
    # st.write(f"Общее количество ошибок: {total_errors}")
    st.metric(label="Общее количество ошибок", value=total_errors)

    # Выводим количество ошибок каждого типа
    # st.write("Количество ошибок по типам:")
    # for error_type, count in error_types_count.items():
    #     st.write(f"{error_type}: {count}")

    # Преобразование списка ошибок в DataFrame
    df_errors = pd.DataFrame(errors)
    df_errors.rename(
        columns={"error_type": "Тип ошибки", "error_text": "Текст ошибки"}, inplace=True
    )
    # Вывод таблицы ошибок в Streamlit
    st.table(df_errors)
    # Выводим ошибки красивым образом
    # st.write("Детали ошибок:")
    # for error in errors:
    #     st.error(
    #         f"Тип ошибки: {error['error_type']}" + ' \n ' + f"Текст ошибки: {error['error_text']}")
