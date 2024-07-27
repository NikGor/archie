import os
import json
import logging
from dotenv import load_dotenv
import pdfplumber
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

prompt_template = """
Given the text of a document, extract key information and format it as a JSON object. Include the following fields:
- "organization": name of the organization that issued the document,
- "date": the date when the document was issued in the format YYYY-MM-DD,
- "title": the title of the document,
- "category": the type of the document (e.g., bank, insurance, invoice, tax, contract, etc.).
- "text": a brief description of the document content in russian.

Ensure that the output is strictly in JSON format. Here is the text of the document:

{document_text}

Please format the response exactly as described.
"""

llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini")

prompt = PromptTemplate.from_template(prompt_template)

chain = (
        RunnablePassthrough()
        | prompt
        | llm
        | JsonOutputParser()
)


def extract_text_from_pdf(pdf_path):
    """Извлечение текста из PDF файла."""
    logging.info(f"Начало извлечения текста из PDF: {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        all_text = ""
        for page in pdf.pages:
            all_text += page.extract_text() + "\n"
    logging.info("Извлечение текста завершено")
    return all_text


def analyze_document_with_gpt(document_text):
    """Анализ текста документа с использованием GPT-4 и возврат JSON."""
    response = chain.invoke({"document_text": document_text})
    logging.info(f"Ответ GPT-4: {response}")

    try:
        extracted_data = response
        logging.info("Анализ текста завершен")
        return extracted_data
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка формата JSON: {e}")
        return None


def main(pdf_path):
    logging.info(f"Начало обработки PDF файла: {pdf_path}")
    document_text = extract_text_from_pdf(pdf_path)
    document_info = analyze_document_with_gpt(document_text)
    logging.info("Обработка завершена")
    return document_info


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(current_dir, '../../documents/samples/ETicket.pdf')

    document_info = main(pdf_path)
    if document_info:
        print(json.dumps(document_info, indent=2, ensure_ascii=False))
    else:
        logging.error("Не удалось извлечь информацию из документа.")
