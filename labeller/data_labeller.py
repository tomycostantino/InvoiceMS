import fitz
import csv
import typing
import os
import ast
import math
import operator
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
import bisect


class DataLabeller:
    def __init__(self):
        '''
        Constructor
        '''

        # this will be the fitz document and will change as we iterate through the directory
        self._current_pdf = ''

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

    def _read_csv(self, file):
        '''
        will get all rows from the csv that contains the data present in the invoices
        :param file:
        :return:
        '''

        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            self._rows = [row for row in reader]

    def _open_pdf(self, file):
        '''
        will be used when one pdf is labelled and the next one comes in.
        :param file:
        :return:
        '''

        self._current_pdf_filename = file
        self._current_pdf = fitz.open(self._pdf_input_path + '/' + file)

    '''
    The following four functions are used to calculate the the sub rectangle in which the words are present
    '''
    def _find_x0(self, values):
        '''
        :param values:
        :return:
        '''

        return min(values)

    def _find_y0(self, values):
        '''
        :param values:
        :return:
        '''

        return min(values)

    def _find_x1(self, values):
        '''
        :param values:
        :return:
        '''

        return max(values)

    def _find_y1(self, values):
        '''
        :param values:
        :return:
        '''

        return max(values)

    def _find_coordinates(self, page, words: typing.List):
        '''
        If found anything, it will return a dictionary containing the word as key and the coordinates as value
        example: {'invoice': (x0, y0, x1, y1)}
        :param page:
        :param words:
        :return:
        '''

        word_coordinates = {}

        # get all words present in pages
        word_list = page.get_text('words')

        # go through all words and see which ones match
        for word in word_list:
            # if the word string is has not been found on the document
            if words.__contains__(word[4]) and word not in self._already_found:
                word_coordinates[word[4]] = word[:4]

                #  add it to the found list, but add the object so it is not re-marked again
                self._already_found.append(word)

        return word_coordinates if word_coordinates else None

    def _find_subrectangle(self, locations: dict):
        '''
        Find the x0, y0, x1, y1 values where the section desired is present
        :param locations:
        :return:
        '''

        x0s = []
        y0s = []
        x1s = []
        y1s = []

        for value in locations.values():
            x0s.append(value[0])
            y0s.append(value[1])
            x1s.append(value[2])
            y1s.append(value[3])

        subrectangle = (self._find_x0(x0s), self._find_y0(y0s),
                        self._find_x1(x1s), self._find_y1(y1s))

        return subrectangle

    def _handle_item_list(self, value):
        '''
        Item lists are a in a nested list [[]] and they are read as a str by the read_csv function
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

    def _get_individual_words(self, row: dict):
        '''
        Split the information in the csv rows into individual words as the pdf reader retrieves one by one
        :param row:
        :return:
        '''

        values_string = ''

        for value in row.values():
            values_string += value
            values_string += ' '
        return values_string.split(' ')[:-1]  # Don't include the last whitespace at the end

    def _calculate_euclidean_distance(self, w1, w2):
        '''
        Calculate euclidean distance between two points
        :param w1:
        :param w2:
        :return:
        '''

        return math.sqrt(sum([pow((w1[0] - w2[0]), 2), pow((w1[1] - w2[1]), 2),
                              pow((w1[2] - w2[2]), 2), pow((w1[3] - w2[3]), 2)]))

    def _find_shortest_distances(self, target, context, n):
        '''
        Given a word, return the two closest words with the euclidean distance
        :param target:
        :param context:
        :return:
        '''

        '''
        Look into adding a third closest distance, or using manhattan distance
        '''

        sorted_list = []

        # Loop through all the words in the pdf
        for near_word in context:
            # only pass the coordinates to calculator
            dist = self._calculate_euclidean_distance(target[:4], near_word[:4])
            # insert into the list and sort it by the value of the dist
            bisect.insort(sorted_list, (near_word[:5], dist), key=lambda x: x[1])

        # don't include the first element as it will be 0 because of being same word
        return sorted_list[1:n+1]

    def _get_context(self, words):
        '''
        Given a word, get the context, in this case the two shortest distances
        :param words:
        :return:
        '''

        context = {}
        for idx, word in enumerate(words):
            context[word[:5]] = self._find_shortest_distances(word, words, 5)

        return context

    def _determine_label(self):
        pass

    def _count_word_occurrences(self, target: str, word_list: typing.List) -> typing.List:
        '''
        see if there is more than one target word in page
        :param target:
        :param word_list:
        :return:
        '''

        occurrences = []
        for word in word_list:
            if target.__contains__(word[4]):
                occurrences.append(word[:5])

        return occurrences

    def _manage_multiple_occurrences(self, target_occurrences: typing.List, csv_str: str, context: dict):
        '''
        If there is multiple occurrences of one word that is a target, then get the whole column and find the other
        relevant words' coordinates and find the target occurrence with the shortest distance
        :param target_occurrences:
        :param csv_str:
        :param word_list:
        :return:
        '''

        relevances = {}

        for key, value in context.items():
            if key in target_occurrences:
                for i in value:
                    if csv_str.find(i[0]) != -1:
                        relevances[key] = i

        return relevances

    def _is_relevant(self, target: str, word_list):
        '''
        If a word in the csv is present in the document then it is relevant so return true
        This will be later filtered out to see which one is the most relevant if there is multiple occurrences
        :param target:
        :param word_list:
        :return:
        '''

        relevant = False
        for word in word_list:
            if word.__contains__(target):
                relevant = True

        return relevant

    def _label_words(self, page, row: dict):
        '''

        :param page:
        :param row:
        :return:
        '''

        # get a list of the words I want to label
        words_to_label = self._get_individual_words(row)

        # get a list of the words on the document
        words_in_page = page.get_text('words')
        context = self._get_context(words_in_page)

        labels = {}

        for word in words_in_page:

            relevant = self._is_relevant(word[4], words_to_label)

            if relevant:
                ocs = self._count_word_occurrences(word[4], words_in_page)

                labels[word[:5]] = {'label': 'relevant',
                                    'word': word,
                                    'context': context[ocs[0]]}

                self._mark_rectangles(page, word[:4], [0, 1, 1, 1])

            else:
                labels[word[:5]] = {'label': 'irrelevant',
                                    'word': word,
                                    'context': context[word[:5]]}
                self._mark_rectangles(page, word[:4])

    def _find_rectangles(self, page, row: dict):
        '''
        This function parses the data label to the sub rectangles where they are present

        data = {'full_name': 'tomas costantino'}

        to_return = {'full_name': (x0,y0,x1,y1),
                     'date': (x0,y0,x1,y1)}
        :param page:
        :param row:
        :return:
        '''

        rectangles = {}

        for key, value in row.items():
            # check if it is item list so convert it to list from str
            if key == 'data':
                value = self._handle_item_list(value)

            elif key == 'total':
                value = '$' + value

            words = self._get_individual_words(row)
            locations = self._find_coordinates(page, words)

            # this means that something has been found in the pdf
            if locations is not None:
                rectangles[key] = self._find_subrectangle(locations)

        return rectangles if rectangles else None
    
    def _mark_rectangles(self, page, rectangles, color = [0, 1, 1, 0]):
        #for value in rectangles:
        #    r = fitz.Rect(value)  # make rect from word bbox
        try:
            page.draw_rect(rectangles, color=color)  # rectangle
            self._current_pdf.save(self._pdf_output_path + '/labelled_' + self._current_pdf_filename)

        except:
            print('couldnt print')
        # once document is finished, clear list
        self._already_found = []

    def _insert_labels(self, page, rectangle: dict):
        for key, value in rectangle.items():
            text_lenght = fitz.get_text_length(key, fontname="Times-Roman", fontsize=10)
            page.insert_textbox(value, key, fontsize=10,  # choose fontsize (float)
                               fontname="Times-Roman",  # a PDF standard font
                               fontfile=None,  # could be a file on your system
                               align=0)  # 0 = left, 1 = center, 2 = right

    def _match_pdfname_to_row(self):
        # pdf name must be the pdf number so it matches the row
        pdf_name = self._current_pdf_filename.split('.')[0]
        return self._rows[int(pdf_name) - 1]

    def _label_document(self):
        row = self._match_pdfname_to_row()
        for page in self._current_pdf.pages():
            self._label_words(page, row)
            rectangles = self._find_rectangles(page, row)
            self._mark_rectangles(page, rectangles) if rectangles else None

    def _create_csv(self):
        pass

    def run(self):
        self._read_csv('/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoice_creation/invoice_template_1/dt.csv')
        self._pdf_input_path = '/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoice_creation/invoice_template_1/generated_pdf'

        # create path for labelled pdfs
        directory_name = self._pdf_input_path.split('/')[-1]
        self._pdf_output_path = self._pdf_input_path.replace(directory_name, 'labelled_pdf')
        os.makedirs(self._pdf_output_path, exist_ok=True)

        # run through all files in the directory
        for file in os.listdir(self._pdf_input_path):
            if file.endswith('.pdf'):
                # make the class change pdfs as we loop through the directory files
                self._open_pdf(file)

                # draw rectangles in pdf
                self._label_document()

        # print out the dataset
        self._create_csv()


def main():

    lab = DataLabeller()
    lab.run()


if __name__ == '__main__':
    main()
