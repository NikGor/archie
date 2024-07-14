import os
import json
import logging
from dotenv import load_dotenv
from openai import OpenAI
import pdfplumber

# Загрузка переменной API_KEY из .env файла
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Инициализация клиента OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Промпт для GPT-4
prompt_template = """
Given the text of a document, extract key information and format it as a JSON object. Include the following fields:
- "organization": name of the organization that issued the document,
- "date": the date when the document was issued,
- "title": the title of the document,
- "category": the type of the document (e.g., bank, insurance, invoice, tax, contract, etc.).

Ensure that the output is strictly in JSON format. Here is the text of the document:

{document_text}

Please format the response exactly as described.
"""


def extract_text_from_pdf(pdf_path):
    """Извлечение текста из PDF файла."""
    logging.info(f"Начало извлечения текста из PDF: {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        all_text = ""
        for page in pdf.pages:
            all_text += page.extract_text() + "\n"
    logging.info("Извлечение текста завершено")
    return all_text


def analyze_document_with_gpt(document_text, attempt=1, max_attempts=3):
    """Анализ текста документа с использованием GPT-4 и возврат JSON."""
    if attempt > max_attempts:
        logging.error("Достигнуто максимальное количество попыток анализа.")
        return None

    logging.info(f"Начало анализа текста документа с использованием GPT-4, попытка {attempt}")
    prompt = prompt_template.format(document_text=document_text)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Логируем полный ответ для отладки
    response_content = response.choices[0].message.content.strip()
    logging.info(f"Ответ GPT-4: {response_content}")

    try:
        extracted_data = json.loads(response_content)
        logging.info("Анализ текста завершен")
        return extracted_data
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка формата JSON: {e}")
        return analyze_document_with_gpt(document_text, attempt + 1)


def main(pdf_path):
    logging.info(f"Начало обработки PDF файла: {pdf_path}")
    document_text = extract_text_from_pdf(pdf_path)
    if "Lorem Ipsum" in document_text:
        logging.error("Документ содержит 'Lorem Ipsum' текст и не может быть проанализирован.")
        return None

    document_info = analyze_document_with_gpt(document_text)
    logging.info("Обработка завершена")
    return document_info


# Пример вызова функции
if __name__ == "__main__":
    # Определение относительного пути к документу
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(current_dir, '../../documents/samples/invoicetome.pdf')

    document_info = main(pdf_path)
    if document_info:
        print(json.dumps(document_info, indent=2, ensure_ascii=False))
    else:
        logging.error("Не удалось извлечь информацию из документа.")
