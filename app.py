import re
from io import StringIO

import streamlit as st
from annotated_text import annotated_text
import fitz
from src import check_main_rules, correct_incorrectly_spaced_dates, find_incorrectly_spaced_dates, check_paragraphs_not_start_with_symbols, check_headers, check_paragraphs_start, check_article_numbering, find_incorrect_dates, highlight_errors, remove_footnotes, title_check, display_errors_with_streamlit, display_title_check_res
from docx import Document

st.set_page_config(
    page_title="LawTechChecker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Создание переменных session state
if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""

if "output_text" not in st.session_state:
    st.session_state["output_text"] = ""

if "title_check_res" not in st.session_state:
    st.session_state["title_check_res"] = ""

if "errors_in_text" not in st.session_state:
    st.session_state["errors_in_text"] = []

if "output_text_with_errors" not in st.session_state:
    st.session_state["output_text_with_errors"] = []

# Functions


def reset_session_state():
    st.session_state["input_text"] = ""
    st.session_state["output_text"] = ""
    st.session_state["title_check_res"] = ""
    st.session_state["errors_in_text"] = []
    st.session_state["output_text_with_errors"] = []


def read_text_file(uploaded_file):
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    # To read file as string:
    return stringio.read()


def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)


# Sidebar
with st.sidebar:
    st.title("🗂 Ввод данных")

    tab1, tab2 = st.tabs(["📁 Данные из файла", "📝 Ввести вручную"])
    with tab1:
        # Вкладка с загрузкой файла, выбором порога и кнопкой предсказания (вкладка 1)
        uploaded_file = st.file_uploader(
            # "txt", "pdf", "docx"
            "Выбрать DOCX файл", type=["docx"], on_change=reset_session_state
        )
        if uploaded_file is not None:
            check_buton = st.button(
                "Проверить на ошибки",
                type="primary",
                use_container_width=True,
                key="button1",
            )
            if uploaded_file.name.endswith(".pdf"):
                pdf_file = fitz.open(stream=uploaded_file.read())
                for page in pdf_file:
                    text = page.get_text("text")
                    st.session_state["input_text"] += text
            elif uploaded_file.name.endswith(".txt"):
                st.session_state["input_text"] = read_text_file(uploaded_file)
            else:
                st.session_state["input_text"] = extract_text_from_docx(
                    uploaded_file)

            if check_buton:
                # Предсказание и сохранение в session state

                st.session_state["errors_in_text"] = find_incorrectly_spaced_dates(
                    st.session_state["input_text"]
                )

                st.session_state["output_text"] = correct_incorrectly_spaced_dates(
                    st.session_state["input_text"]
                )

                st.session_state["output_text"] = remove_footnotes(
                    st.session_state["output_text"]
                )
                st.session_state["errors_in_text"] += find_incorrect_dates(
                    st.session_state["output_text"]
                )

                # st.session_state["errors_in_text"] = st.session_state["errors_in_text"] + check_article_numbering(
                #     st.session_state["output_text"]
                # )
                # check_main_rules
                st.session_state["errors_in_text"] = st.session_state["errors_in_text"] + check_main_rules(
                    st.session_state["output_text"]
                )

                # check_paragraphs_start, check_headers
                # st.session_state["errors_in_text"] = st.session_state["errors_in_text"] + check_paragraphs_start(
                #     st.session_state["output_text"]
                # )
                # st.session_state["errors_in_text"] = st.session_state["errors_in_text"] + check_headers(
                #     st.session_state["output_text"]
                # )
                # error place
                # check_paragraphs_not_start_with_symbols
                st.session_state["errors_in_text"] = st.session_state["errors_in_text"] + check_paragraphs_not_start_with_symbols(
                    st.session_state["output_text"]
                )
                st.session_state["output_text_with_errors"] = highlight_errors(
                    st.session_state["output_text"], st.session_state["errors_in_text"]
                )
                # uncomment this
                # st.session_state["title_check_res"] = title_check(
                #     st.session_state["input_text"][:1000])

# Main section start
# Основной блок
# st.image('https://miro.medium.com/v2/resize:fit:1400/1*WqId29D5dN_8DhiYQcHa2w.png', width=400)
st.title("Проверка юр. техники")

# with st.expander("Описание проекта"):
#     st.write(
#         """
#     В данном проекте мы рассмотрим задачу прогнозирования оттока клиентов.
#     Для этого мы будем использовать датасет из открытых источников.
#     Датасет содержит информацию о клиентах, которые уже ушли или остались в компании.
#     Наша задача - построить модель, которая будет предсказывать отток клиентов.
#     """
#     )

if (
    st.session_state["output_text"] != ""
    and st.session_state["output_text_with_errors"] != []
):
    st.divider()
    st.subheader("Найденные ошибки:")
    # st.json(st.session_state["errors_in_text"])
    display_errors_with_streamlit(st.session_state["errors_in_text"])

    if st.session_state["title_check_res"] != "":
        st.divider()
        display_title_check_res(st.session_state["title_check_res"])
        st.divider()

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.subheader("Входной текст")
        st.write(st.session_state["input_text"])
        # st.text_area("Входной текст",
        #              value=st.session_state["input_text"], height=400)
    with col2:
        st.subheader("Результат")
        # st.write(st.session_state['output_text'])
        annotated_text(*st.session_state["output_text_with_errors"])
