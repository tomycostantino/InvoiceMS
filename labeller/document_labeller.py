import fitz
import csv
import typing
import os
import ast
import math
import bisect
import re
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from dataset_generator.dataset_generator_base import DatasetGeneratorBase


class DataLabeller:
    '''
    This class will open all PDF documents in a given folder, and will label them based on the csv data
    that was used to generate the invoices
    '''

    def __init__(self):
        '''
        Constructor
        '''

        # this will be the fitz document and will change as we iterate through the directory
        self._current_pdf = None

        # the filename is kept to write it when outputting labelled doc
        self._current_pdf_filename = ''

        # directory path where to read pdfs
        self._pdf_input_path = ''

        # directory path to store labelled documents
        self._pdf_output_path = ''

        # the class can open multiple documents, when analysing one, store the object that were already found
        # so they are not marked again
        self._already_found = []

        # rows from csv file
        self._rows = []

        # all words from pdf file retrieved with Fitz library
        self._words_in_file = []

        self._context = {}

    def _read_csv(self, file):
        '''
        will get all rows from the csv that contains the data present in the invoices
        :param file:
        :return:
        '''

        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            self._rows = [row for row in reader]

    def _read_pdf(self, file):
        '''
        will be used when one pdf is labelled and the next one comes in.
        :param file:
        :return:
        '''

        self._current_pdf_filename = file
        self._current_pdf = fitz.open(self._pdf_input_path + '/' + file)

        self._get_words_from_pdf()
        self._get_pdf_words_context()

    def _get_words_from_pdf(self):
        '''
        Store all words from pdf in the class object
        :return:
        '''

        self._words_in_file = []

        for page in self._current_pdf.pages():
            self._words_in_file += page.get_text('words')

    def _get_pdf_words_context(self):
        '''
        Given a word, get the context, in this case the shortest distances
        :param words:
        :return:
        '''

        self._context = {}

        for idx, word in enumerate(self._words_in_file):
            self._context[word[:5]] = self._find_shortest_distances(word, 5)

    def _handle_item_list(self, value):
        '''
        Item lists are in a nested list [[]] and they are read as a str by the read_csv function
        so convert it to a literal and process the words
        :param value:
        :return:
        '''

        new_value = ''
        value = ast.literal_eval(value)
        # for item list in value
        for il in value:
            # for each value in the item list
            for val in il:
                # if the value is int, in this case int represents the item number
                if type(val) == int:
                    val = str(val)
                new_value += val
                new_value += ' '

        return new_value[:-1]  # remove the whitespace from the end

    def _split_csv_values_into_words(self, row: dict):
        '''
        Split the information in the csv rows into individual words as the pdf reader retrieves one by one
        :param row:
        :return:
        '''

        values_string = ' '.join(str(value) for value in row.values())
        return values_string.strip().split()

    def _calculate_euclidean_distance(self, w1, w2):
        '''
        Calculate euclidean distance between two points
        :param w1:
        :param w2:
        :return:
        '''

        return math.sqrt(sum([pow((w1[0] - w2[0]), 2), pow((w1[1] - w2[1]), 2),
                              pow((w1[2] - w2[2]), 2), pow((w1[3] - w2[3]), 2)]))

    def _calculate_center(self, coord):
        x_center = (coord[0] + coord[2]) / 2
        y_center = (coord[1] + coord[3]) / 2
        return x_center, y_center

    def _calculate_manhattan_distance(self, coord1, coord2):
        center1 = self._calculate_center(coord1)
        center2 = self._calculate_center(coord2)
        return abs(center1[0] - center2[0]) + abs(center1[1] - center2[1])

    def _find_shortest_distances(self, target, n):
        '''
        Given a word, return the two closest words with the euclidean distance
        :param target:
        :return:
        '''

        sorted_list = []

        # Loop through all the words in the pdf
        for near_word in self._words_in_file:
            # only pass the coordinates to calculator
            dist = self._calculate_euclidean_distance(target[:4], near_word[:4])
            # insert into the list and sort it by the value of the dist
            bisect.insort(sorted_list, (near_word[:5], dist), key=lambda x: x[1])

        # don't include the first element as it will be 0 because of being same word
        return sorted_list[1:n+1]

    def _build_label_dict(self, label: str, word) -> dict:
        '''
        Generates the dict to label a word on the doc
        :param label:
        :param word:
        :return:
        '''

        data = {'label': label,
                'word': word[4],
                'position': (round(word[0], 2), round(word[1], 2), round(word[2], 2), round(word[3], 2))
                }
        for i, item in enumerate(self._context[word[:5]]):
            data[f'near_word_{i + 1}_word'] = item[0][4]
            data[f'near_word_{i+1}_axes'] = (round(item[0][0], 2), round(item[0][1], 2), round(item[0][2], 2), round(item[0][3], 2))
            data[f'near_word_{i+1}_dist'] = float(round(item[1], 2))

        return data

    def _count_word_occurrences(self, target: str) -> typing.List:
        '''
        see if there is more than one target word in page
        :param target:
        :return:
        '''

        # Create a regex pattern for the target word, allowing any number of spaces,
        # hyphens, or line breaks between the parts
        target_pattern = re.compile('-|\\s+|\n'.join(re.escape(part) for part in target.split('-')))

        occurrences = []
        for word in self._words_in_file:
            if target_pattern.match(word[4]):
                occurrences.append(word[:5])

        return occurrences

    def _get_cosine_similarity(self, text1, text2):
        documents = [text1, text2]
        count_vectorizer = CountVectorizer().fit_transform(documents)
        vectors = count_vectorizer.toarray()
        return cosine_similarity(vectors)[0][1]

    def _get_context_indices(self, occurrence):
        """
        Given an occurrence, find the indices of the context words in self._words_in_file.
        :param occurrence: the occurrence for which the context is to be found
        :return: a tuple of the form (start_index, end_index)
        """
        index = -1
        for i, word in enumerate(self._words_in_file):
            if word[4] == occurrence[4]:
                index = i
                break

        if index == -1:
            raise ValueError(f"Occurrence not found in self._words_in_file: {occurrence}")

        context_start = max(0, index - 5)
        context_end = min(len(self._words_in_file), index + 6)
        return context_start, context_end

    def _calculate_context_similarity(self, context_string, csv_fields):
        """
        Calculate the similarity between the context string and the csv fields using Jaccard similarity.
        :param context_string: the context string
        :param csv_fields: the list of csv field values
        :return: the Jaccard similarity between the context string and the csv fields
        """
        context_set = set(context_string.lower().split())
        csv_fields_set = set(' '.join(csv_fields).lower().split())

        intersection = len(context_set.intersection(csv_fields_set))
        union = len(context_set.union(csv_fields_set))

        similarity = intersection / union if union > 0 else 0
        return similarity

    def _manage_multiple_occurrences(self, occurrences: typing.List, csv_fields):
        '''
        If there is multiple occurrences of one word that is a target, then get the whole column and find the other
        relevant words' coordinates and find the target occurrence with the shortest distance
        :param occurrences:
        :param csv_fields:
        :return:
        '''

        highest_similarity = -1
        most_relevant_occurrence = None

        for occurrence in occurrences:
            context_start, context_end = self._get_context_indices(occurrence)
            context_words = self._words_in_file[context_start:context_end]
            context_string = ' '.join(word[4] for word in context_words)

            similarity = self._calculate_context_similarity(context_string, csv_fields)

            if similarity > highest_similarity:
                highest_similarity = similarity
                most_relevant_occurrence = occurrence

        return most_relevant_occurrence

    def _is_relevant(self, target: str, word_list):
        '''
        If a word in the csv is present in the document then it is relevant so return true
        This will be later filtered out to see which one is the most relevant if there is multiple occurrences
        :param target:
        :param word_list:
        :return:
        '''

        for word in word_list:
            if word == target:
                return True

            # Check if the target is a substring at the beginning or end of the word
            if word.startswith(target) or word.endswith(target):
                return True

        return False

    def _label_words(self, row: dict):
        '''
        will put a label to each individual word
        :param page:
        :param row:
        :return:
        '''

        # get a list of the words I want to label
        individual_words_to_label = self._split_csv_values_into_words(row)
        csv_fields = [str(val) for val in row.values()]

        label_rows = []

        # Loop through all words in document to find the ones to label
        for word in self._words_in_file:
            labelled_word = {}
            # if the word in the pdf matches the one in the csv then it is relevant
            if self._is_relevant(word[4], individual_words_to_label):
                # if there is more than one occurence, it must be dealt with
                n_occurrences = self._count_word_occurrences(word[4])

                # if it is there only one time then it is relevant and just be labelled as such
                if len(n_occurrences) > 0:
                    labelled_word = self._build_label_dict('relevant', word)

                else:
                    ''' Gotta keep working on this'''
                    relevant_occurrence = self._manage_multiple_occurrences(n_occurrences, csv_fields)
                    labelled_word = self._build_label_dict('relevant' if word == relevant_occurrence else 'irrelevant', word)

            else:
                labelled_word = self._build_label_dict('irrelevant', word)

            if labelled_word['label'] == 'relevant':
                self._mark_rectangles(word[:4], [0, 1, 1, 1])
            else:
                self._mark_rectangles(word[:4])

            label_rows.append(labelled_word)

        return label_rows

    def _mark_rectangles(self, rectangles, color = [0, 1, 1, 0]):
        for page in self._current_pdf.pages():
            try:
                page.draw_rect(rectangles, color=color)  # rectangle
                self._current_pdf.save(self._pdf_output_path + '/labelled_' + self._current_pdf_filename)

            except ValueError:
                print('couldnt print')
        # once document is finished, clear list
        # self._already_found = []

    def _match_pdfname_to_row(self):
        '''
        pdf name must be the pdf number so it matches the row
        :return:
        '''

        pdf_name = self._current_pdf_filename.split('.')[0]
        return self._rows[int(pdf_name) - 1]

    def _label_document(self):
        '''
        Will label doc by doc
        :return:
        '''

        row = self._match_pdfname_to_row()  # if we are reading '80.pdf' then retrieve data from 80th row
        labels = self._label_words(row)
        self._append_to_csv(labels)

    def _append_to_csv(self, labels):
        '''
        Append new rows into csv file
        :param labels:
        :return:
        '''

        ds = DatasetGeneratorBase()
        fieldnames = list(labels[0].keys())
        # fieldnames = list(fieldnames[0].keys())  # get fieldnames
        ds.write_csv('../datasets/dataset.csv', fieldnames, labels, 'a')

    def run(self):
        '''
        Run the labelling process
        :return:
        '''

        self._read_csv('/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoice_creation/invoice_template_1/dt.csv')
        self._pdf_input_path = '/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoice_creation/invoice_template_1/generated_pdf'

        # create path for labelled pdfs
        directory_name = self._pdf_input_path.split('/')[-1]
        self._pdf_output_path = self._pdf_input_path.replace(directory_name, 'labelled_pdf_second')
        os.makedirs(self._pdf_output_path, exist_ok=True)

        # run through all files in the directory
        for file in os.listdir(self._pdf_input_path):
            if file.endswith('.pdf'):

                # make the class change pdfs as we loop through the directory files
                self._read_pdf(file)

                # do the labelling
                self._label_document()


def main():

    lab = DataLabeller()
    lab.run()


if __name__ == '__main__':
    main()
