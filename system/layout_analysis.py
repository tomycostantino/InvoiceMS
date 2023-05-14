from pdf_layout_scanner import layout_scanner
from gpt_key import api_key

# Kor!
from kor.extraction import create_extraction_chain
from kor.nodes import Object, Text, Number

# LangChain Models
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

# Standard Helpers
import pandas as pd
import requests
import time
import json
from datetime import datetime

# Text Helpers
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# For token counting
from langchain.callbacks import get_openai_callback


def printOutput(output):
    print(json.dumps(output,sort_keys=True, indent=3))


# It's better to do this an environment variable but putting it in plain text for clarity
openai_api_key = api_key


llm = ChatOpenAI(
    model_name="gpt-3.5-turbo", # Cheaper but less reliable
    # model_name="gpt-4",
    temperature=0,
    max_tokens=2000,
    openai_api_key=openai_api_key
)


def extract_information(text):
    invoice_schema = Object(
        id="invoice",
        description="Invoice information",
        attributes=[
            Text(
                id="company_issuer",
                description="The company that issued the invoice.",
            ),
            Text(
                id="person_billed",
                description="The person to whom the invoice is billed.",
            ),
            Text(
                id="date",
                description="The date when the invoice was issued, which could be in various formats such as DD-MM-YYYY, MM/DD/YYYY, or spelled out like '11th September, 2019'.",
            ),
            Number(
                id="invoice_number",
                description="The invoice number, which is typically a long unique number associated with the invoice.",
            )
        ],

        examples=[
            ("Invoice from Apple Inc. dated 01-03-2023, issued to John Doe. Invoice number 12345.",
             [{"company_issuer": "Apple Inc."}, {"person_billed": "John Doe"}, {"date": "01-03-2023"},
              {"invoice_number": 12345}]),
            ("John Doe received an invoice numbered 23456 from Microsoft Corp. on 02-04-2023.",
             [{"company_issuer": "Microsoft Corp."}, {"person_billed": "John Doe"}, {"date": "02-04-2023"},
              {"invoice_number": 23456}]),
            ("INVOICE\nTurner and Sons\nInvoice No: 42965846\nDate: 11 September, 2019\nBill to: Lewis and Sons",
             [{"company_issuer": "Turner and Sons"}, {"person_billed": "Lewis and Sons"},
              {"date": "11 September, 2019"}, {"invoice_number": 42965846}])
        ]
    )

    chain = create_extraction_chain(llm, invoice_schema)

    output = chain.predict_and_parse(text=(text))["data"]

    printOutput(output)
    # Notice how there isn't "spot" in the results list because it's the name of a dog, not a person.


if __name__ == '__main__':
    pages = layout_scanner.get_pages(
        '/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoices/invoice_template_3/generated_pdf/1.pdf'
        )
    a = '/Users/tomasc/PycharmProjects/IMS/invoices_templates/PDF/10.pdf'

    # a string of all the text on the first page
    print(pages[0])

    extract_information(pages[0])

