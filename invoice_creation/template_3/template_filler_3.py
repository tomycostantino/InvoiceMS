import os
import pandas as pd
import json
from docxtpl import DocxTemplate


def generate_invoice(template_path, data, output_dir):
    template = DocxTemplate(template_path)

    context = {
        "issuer": data["issuer"],
        "issuer_address": data["issuer_address"],
        "issuer_number": data["issuer_number"],
        "business_code": data["business_code"],
        "invoice_n": data["invoice_n"],
        "date": data["date"],
        "billed_to": data["billed_to"],
        "email": data["email"],
        "website": data["website"],
        "deadline": data["deadline"],
        "data": data["data"],
        "subtotal": data["subtotal"],
        "tax": data["tax"],
        "total": data["total"],
    }

    template.render(context)
    output_path = os.path.join(output_dir, f"invoice_{data['invoice_n']}.docx")
    template.save(output_path)


def read_data_from_csv(file_path):
    df = pd.read_csv(file_path)
    data = []
    for index, row in df.iterrows():
        invoice_data = {
            "issuer": row["issuer"],
            "issuer_address": row["issuer_address"],
            "issuer_number": row["issuer_number"],
            "business_code": row["business_code"],
            "invoice_n": row["invoice_n"],
            "date": row["date"],
            "billed_to": row["billed_to"],
            "email": row["email"],
            "website": row["website"],
            "deadline": row["deadline"],
            "data": json.loads(row['data']),
            "subtotal": row["subtotal"],
            "tax": row["tax"],
            "total": row["total"],
        }
        data.append(invoice_data)

    return data


csv_file_path = "data.csv"  # Replace with your CSV file path
word_template_path = "3.docx"  # Replace with your Word template path
output_dir = "generated_docx"  # Replace with the desired output directory

os.makedirs(output_dir, exist_ok=True)

data_list = read_data_from_csv(csv_file_path)
for data in data_list:
    generate_invoice(word_template_path, data, output_dir)
