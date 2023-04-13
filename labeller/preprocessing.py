import fitz
import string
import spacy
import pandas as pd
from nltk.corpus import stopwords


class PreProcessing:
    def __init__(self):
        pass

    def extract_text_with_coordinates(self, pdf_file):
        doc = fitz.open(pdf_file)
        data = []

        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block["type"] == 0:  # 0 means text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            for i, word in enumerate(span["text"].split()):
                                data.append({
                                    "word": word,
                                    "coordinates": span["bbox"] if i == 0 else None
                                    # assuming no change in the bbox for other words in the same span
                                })
        doc.close()
        return data

    def remove_punctuation(self, word):
        return word.translate(str.maketrans("", "", string.punctuation))

    def remove_stopwords(self, word):
        stop_words = set(stopwords.words('english'))
        return word if word not in stop_words else None

    def lemmatize(self, word):
        if not word:
            return word

        nlp = spacy.load("en_core_web_sm")
        return nlp(word)[0].lemma_

    def read_csv(self, path):
        return pd.read_csv(path)

    def create_mapping(self):
        mapping = {}
        csv_data = self.read_csv('')
        for index, row in csv_data.iterrows():
            word = row['word']
            label = row['label']
            mapping[word] = label
        return mapping

    def assign_labels(self,  preprocessed_data, mapping):
        labeled_data = []
        for item in preprocessed_data:
            word = item['word']
            label = mapping.get(word, 'O')
            labeled_data.append({
                'word': word,
                'label': label,
                'coordinates': item['coordinates']
            })
        return labeled_data

    def preprocess_data(self, data):

        preprocessed_data = []

        for item in data:
            word = item["word"]

            # Convert to lowercase
            word = word.lower()

            # Remove punctuation
            word = self.remove_punctuation(word)

            # Remove stop words
            word = self.remove_stopwords(word)
            if word is None:
                continue

            # Lemmatize
            word = self.lemmatize(word)

            # Standardize numbers

            # word = standardize_numbers(word)

            # Add other preprocessing steps as needed

            preprocessed_data.append({
                "word": word,
                "coordinates": item["coordinates"]
            })

        return preprocessed_data


if __name__ == '__main__':
    pp = PreProcessing()
    data = pp.extract_text_with_coordinates('/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoice_creation/invoice_template_2/generated_pdf/1.pdf')
    print(pp.preprocess_data(data))
