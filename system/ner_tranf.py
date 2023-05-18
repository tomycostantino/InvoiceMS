from document_processing.pdf_reader import PDFDataReader
from transformers import AutoTokenizer, AutoModelForTokenClassification

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("xooca/roberta_ner_personal_info")
model = AutoModelForTokenClassification.from_pretrained("xooca/roberta_ner_personal_info")


# Define a function to make predictions
def predict(text):
    # Tokenize the input text
    inputs = tokenizer.encode_plus(text, return_tensors="pt")

    # Make predictions with the model
    outputs = model(**inputs)

    # Get the predicted labels
    predicted_labels = outputs.logits.argmax(dim=2)

    # Map the label IDs back to their string representations
    labels = [tokenizer.decode([label_id]) for label_id in predicted_labels[0]]

    # Return the tokenized input text and predicted labels
    return tokenizer.convert_ids_to_tokens(inputs["input_ids"][0]), labels


reader = PDFDataReader()

for text in reader.retrieve_text_blocks(
        '/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoices/invoice_template_1/generated_pdf/1.pdf'):

    if isinstance(text, str):
        tokens, labels = predict(text)
        print(tokens)
        print(labels)
