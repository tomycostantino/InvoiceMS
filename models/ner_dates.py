from flair.data import Sentence
from flair.models import SequenceTagger
from document_processing.pdf_reader import PDFDataReader


if __name__ == "__main__":
    # load tagger
    tagger = SequenceTagger.load("flair/ner-english-large")

    reader = PDFDataReader()

    for text in reader.retrieve_text_blocks(
            '/Users/tomasc/PycharmProjects/IMS/invoices_templates/PDF/10.pdf'):
        if isinstance(text, str):
            # make example sentence
            sentence = Sentence(text)
            # predict NER tags
            tagger.predict(sentence)

            # print sentence
            print(sentence)

            # print predicted NER spans
            print('The following NER tags are found:')

            # iterate over entities and print
            for entity in sentence.get_spans('ner'):
                print(entity)


document = lp.Document(file_path='/Users/tomasc/PycharmProjects/IMS/invoices_templates/PDF/10.pdf')

plt.imshow(document.visualize())
plt.show()

layout = document.get_layout()

text = document.get_text()

tables = lp.detect_tables(document, model_type='table')

plt.imshow(lp.visualize_tables(document, tables))
plt.show()
