import fitz
import csv
import typing
import os
import ast
import math
import operator


class DataLabeller:
    def __init__(self):
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
        # will get all rows from the csv that contains the data present in the invoices
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            self._rows = [row for row in reader]

    def _open_pdf(self, file):
        # will be used when one pdf is labelled and the next one comes in.
        self._current_pdf_filename = file
        self._current_pdf = fitz.open(self._pdf_input_path + '/' + file)

    '''
    The following four functions are used to calculate the the sub rectangle in which the words are present
    '''
    def _find_x0(self, values):
        return min(values)

    def _find_y0(self, values):
        return min(values)

    def _find_x1(self, values):
        return max(values)

    def _find_y1(self, values):
        return max(values)

    def _split_into_words(self, value: str):
        '''
        When getting a value, split it into individual words as Fitz library will analyse pdf word by word
        '''
        # get the words one by one and return a list
        if value.__contains__('-'):
            value = value.replace('-', '- ')
        return [v for v in value.split(' ')]

    def _find_coordinates(self, page, words: typing.List):
        '''
        If found anything, it will return a dictionary containing the word as key and the coordinates as value
        example: {'invoice': (x0, y0, x1, y1)}
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
        values_string = ''

        for value in row.values():
            values_string += value
            values_string += ' '
        return values_string.split(' ')[:-1]  # Don't include the last whitespace at the end

    def _find_cw1(self):
        pass

    def _find_cw2(self):
        pass

    def _find_edcw1(self):
        pass

    def _find_edcw2(self):
        pass

    def _calculate_distance(self, w1, w2):
        return math.sqrt(sum([pow((w1[0] - w2[0]), 2), pow((w1[1] - w2[1]), 2),
                              pow((w1[2] - w2[2]), 2), pow((w1[3] - w2[3]), 2)]))

    def _euclidean_distance(self, target, near_words):
        distance_to_target = {}

        for near_word in near_words:
            # only pass the coordinates to calculator
            distance_to_target[near_word] = self._calculate_distance(target[:4], near_word[:4])

        return distance_to_target

    def _get_context(self, words):
        context = {}
        for idx, word in enumerate(words):
            # check within ranges
            if idx - 2 >= 0 and idx + 2 <= len(words):
                sublist = words[idx-2:idx+3]
                sublist.pop(idx)
                distances = self._euclidean_distance(word, sublist)
                values_list = [value for value in distances.values()]
                nearest_values = sorted(values_list)
                context[word] = nearest_values[:2]

            print(context)

    def _determine_label(self):
        pass

    def _label_words(self, page, row: dict):
        # get a list of the words I want to label
        words_to_label = self._get_individual_words(row)

        # get a list of the words on the document
        words_in_file = page.get_text('words')
        self._get_context(words_in_file)

        labelled_words = {}

        for word in words_in_file:
            label = 0
            cw1, edcw1, cw2, edcw2 = 0, 0, 0, 0
            labelled_words[word[:4]] = {'label': label,
                                        'word': word[4],
                                        'cw1': cw1,
                                        'cw2': cw2,
                                        'eccw1': edcw1,
                                        'eccw2': edcw2}

    def _find_rectangles(self, page, row: dict):
        '''
        This function parses the data label to the sub rectangles where they are present

        data = {'full_name': 'tomas costantino'}

        to_return = {'full_name': (x0,y0,x1,y1),
                     'date': (x0,y0,x1,y1)}
        '''
        rectangles = {}

        for key, value in row.items():
            # check if it is item list so convert it to list from str
            if key == 'data':
                value = self._handle_item_list(value)

            elif key == 'total':
                value = '$' + value

            words = self._split_into_words(value)
            locations = self._find_coordinates(page, words)

            # this means that something has been found in the pdf
            if locations is not None:
                rectangles[key] = self._find_subrectangle(locations)

        return rectangles if rectangles else None

    def _mark_rectangles(self, page, rectangles):
        for value in rectangles.values():
            r = fitz.Rect(value)  # make rect from word bbox
            page.draw_rect(r, color=[0, 1, 1, 0])  # rectangle
        self._current_pdf.save(self._pdf_output_path + '/labelled_' + self._current_pdf_filename)
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
