import spacy
from document_processing.pdf_reader import PDFDataReader


def load_model(model_path):
    """Load a trained model."""
    return spacy.load(model_path)


def predict(model, text):
    """Use a trained model to make predictions."""
    doc = model(text)
    entities = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
    return entities


if __name__ == "__main__":
    reader = PDFDataReader()
    model_path = "/Users/tomasc/PycharmProjects/IMS/InvoiceMS/models"
    model = load_model(model_path)

    for text in reader.retrieve_text_blocks('/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoices/invoice_template_1/generated_pdf/1.pdf'):
        if isinstance(text, str):
            predictions = predict(model, text)

            for start, end, label in predictions:
                print(f"Entity: {text[start:end]}, Label: {label}")
