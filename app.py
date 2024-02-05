import re
import streamlit as st
from io import StringIO
from annotated_text import annotated_text

st.set_page_config(
    page_title="LawTechChecker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Создание переменных session state
if 'input_text' not in st.session_state:
    st.session_state['input_text'] = ''

# Functions


def read_text_file(uploaded_file):
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    # To read file as string:
    return stringio.read()


# Sidebar
with st.sidebar:
    st.title('🗂 Ввод данных')

    tab1, tab2 = st.tabs(['📁 Данные из файла', '📝 Ввести вручную'])
    with tab1:
        # Вкладка с загрузкой файла, выбором порога и кнопкой предсказания (вкладка 1)
        uploaded_file = st.file_uploader("Выбрать CSV файл", type=[
                                         'txt', 'pdf'], on_change=None)
        if uploaded_file is not None:
            check_buton = st.button(
                'Проверить на ошибки', type='primary', use_container_width=True, key='button1')
            st.session_state['input_text'] = read_text_file(uploaded_file)
            if check_buton:
                # Предсказание и сохранение в session state
                print('Проверка файла')

# Main section start
# Основной блок
# st.image('https://miro.medium.com/v2/resize:fit:1400/1*WqId29D5dN_8DhiYQcHa2w.png', width=400)
st.title('Проверка юр. техники')

with st.expander("Описание проекта"):
    st.write("""
    В данном проекте мы рассмотрим задачу прогнозирования оттока клиентов.
    Для этого мы будем использовать датасет из открытых источников.
    Датасет содержит информацию о клиентах, которые уже ушли или остались в компании.
    Наша задача - построить модель, которая будет предсказывать отток клиентов.
    """)

if st.session_state['input_text'] != '':
    col1, col2 = st.columns(2, gap='medium')
    with col1:
        st.subheader('Входной текст')
        st.write(st.session_state['input_text'])
    with col2:
        st.subheader('Результат')

        annotated_text(
            "This ",
            ("is", "", "#fea"),
            " some ",
            ("annotated", "adj"),
            ("text", "noun"),
            " for those of ",
            ("you", "pronoun"),
            " who ",
            ("like", "verb"),
            " this sort of ",
            ("thing", "noun"),
            "."
        )
