import fitz
import csv
import typing
import os
import ast


class DataLabeller:
    def __init__(self):
        self._pdf_file = ''
        self._pdf_filename = ''

        self._input_path = ''

        self._output_path = ''

        self._already_found = []

        # open csv file
        self._rows = []

    def _read_csv(self, file):
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            self._rows = [row for row in reader]

    def _open_pdf(self, file):
        # will be used when one pdf is labelled and the next one comes in.
        self._pdf_filename = file
        self._pdf_file = fitz.open(self._input_path + '/' + file)

    def _find_x0(self, values):
        return min(values)

    def _find_y0(self, values):
        return min(values)

    def _find_x1(self, values):
        return max(values)

    def _find_y1(self, values):
        return max(values)

    def _get_words(self, value: str):
        # get the words one by one and as a list
        if value.__contains__('-'):
            value = value.replace('-', '- ')
        return [v for v in value.split(' ')]

    def _find_words(self, page, words: typing.List):
        # it will be a dictionary with the key as the word string and the value
        # will be the word's x0,y0,x1,y1 values
        word_coordinates = {}

        # get all words present in pages
        word_list = page.get_text('words')

        # go through all words and see which ones match
        for word in word_list:
            # check list isn't empty, if it is then there is no need to keep looking
            if words:
                # if the word string is in the list
                if words.__contains__(word[4]) and word not in self._already_found:
                    word_coordinates[word[4]] = word[:4]
                    # once word is found, remove it from the list to be found
                    words.remove(word[4])
                    # now add it to the found list, but this time add the object
                    # so it is not re-marked again
                    self._already_found.append(word)

            # when found all words bail out
            else:
                break

        return word_coordinates if word_coordinates else None

    def _find_subrectangle(self, locations: dict):
        x0s = []
        y0s = []
        x1s = []
        y1s = []
        for value in locations.values():
            # need to work on this
            x0s.append(value[0])
            y0s.append(value[1])
            x1s.append(value[2])
            y1s.append(value[3])

        subrectangle = (self._find_x0(x0s), self._find_y0(y0s),
                        self._find_x1(x1s), self._find_y1(y1s))

        return subrectangle

    def _handle_item_list(self, value):
        new_value = ''
        value = ast.literal_eval(value)
        for il in value:
            for val in il:
                if type(val) == int:
                    val = str(val)
                new_value += val
                new_value += ' '

        return new_value

    def _find_rectangles(self, page, row: dict):
        # data = {'full_name': 'tomas costantino'}
        # to_return = {'full_name': (x0,y0,x1,y1),
        #              'date': (x0,y0,x1,y1)}

        rectangles = {}

        for key, value in row.items():
            # check if it is item list so convert it to list from str
            if key == 'data':
                value = self._handle_item_list(value)

            words = self._get_words(value)
            locations = self._find_words(page, words)

            if locations is not None:
                rectangles[key] = self._find_subrectangle(locations)

        return rectangles if rectangles else None

    def _mark_rectangles(self, page, rectangles):
        for value in rectangles.values():
            r = fitz.Rect(value)  # make rect from word bbox
            page.draw_rect(r, color=[0, 1, 1, 0])  # rectangle
        self._pdf_file.save(self._output_path + '/labelled_' + self._pdf_filename)
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
        pdf_name = self._pdf_filename.split('.')[0]
        return self._rows[int(pdf_name) - 1]

    def _label_document(self):
        row = self._match_pdfname_to_row()
        for page in self._pdf_file.pages():
            rectangles = self._find_rectangles(page, row)
            self._mark_rectangles(page, rectangles) if rectangles else None
            # self._insert_labels(page, rectangles)

    def _create_csv(self):
        pass

    def run(self):
        self._read_csv('/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoice_creation/invoice_template_1/dt.csv')
        self._input_path = '/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoice_creation/invoice_template_1/generated_pdf'

        # create path for labelled pdfs
        directory_name = self._input_path.split('/')[-1]
        self._output_path = self._input_path.replace(directory_name, 'labelled_pdf')
        os.makedirs(self._output_path, exist_ok=True)

        # run through all files in the directory
        for file in os.listdir(self._input_path):
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
