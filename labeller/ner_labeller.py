import os
import csv
import time
from document_processing.pdf_reader import PDFDataReader


def read_csv(file):
    '''
    will get all rows from the csv that contains the data present in the invoices
    :param file:
    :return:
    '''

    try:
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]
            f.close()

        return rows

    except Exception as e:
        print(e)
        return e


def match_pdfname_to_row(filename):
    '''
    pdf filename must be the pdf number, so it matches the row
    :return:
    '''

    pdf_name = filename.split('/')[-1]
    pdf_name = pdf_name.split('.')[0]
    return int(pdf_name) - 1


def read_pdf_blocks(file):
    """
    Reads blocks instead of words for NER
    :param file:
    :return:
    """

    data_reader = PDFDataReader()
    data = data_reader.retrieve_text_blocks(file)
    del data_reader
    return data


def label_substring_in_string(string, substring, label):
    start_index = string.find(substring)
    end_index = start_index + len(substring)
    return {
        'entities': [(start_index, end_index, label)]
    }


def label_document(file, row_data):
    """
    Label doc by doc
    :return:
    """
    labels = []

    text_blocks = read_pdf_blocks(file)
    for block in text_blocks:
        if block.lower().__contains__(row_data['issuer'].lower()):
            labels.append(
                (block.lower(), label_substring_in_string(block.lower(), row_data['issuer'].lower(), 'COMPANY')))

        elif block.lower().__contains__(row_data['billed_to'].lower()):
            labels.append(
                (block.lower(), label_substring_in_string(block.lower(), row_data['billed_to'].lower(), 'PERSON')))

        elif block.lower().__contains__(row_data['date'].lower()):
            labels.append(
                (block.lower(), label_substring_in_string(block.lower(), row_data['date'].lower(), 'DATE')))

        else:
            labels.append((block.lower(), {'entities': []}))

    return labels


def run_ner_labelling(data_folder):

    train_data = []

    for folder in os.listdir(data_folder):
        if folder.startswith('invoice'):

            print(f'Labelling {folder} folder')

            # Read data to label pdfs
            rows = read_csv(f'{data_folder}/{folder}/data.csv')

            for file in os.listdir(f'{data_folder}/{folder}/generated_pdf'):
                if file.endswith('.pdf'):

                    start_time = time.time()

                    row_n = match_pdfname_to_row(file)

                    labels = label_document(f'{data_folder}/{folder}/generated_pdf/{file}', rows[row_n])

                    for label in labels:
                        train_data.append(label)

                    # stop clock and print out time taken
                    end_time = time.time()
                    print(f'Time taken to label {file} was {round(end_time - start_time, 5)} seconds')

    return train_data


if __name__ == '__main__':

    td = run_ner_labelling('../invoices')
