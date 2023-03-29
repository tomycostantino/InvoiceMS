import fitz
import csv
import typing
import os


class DataLabeller:
    def __init__(self):
        self._pdf_file = ''
        self._pdf_filename = ''

        self._input_path = ''

        self._output_path = ''

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
        return [v for v in value.split(' ')]

    def _find_words(self, words: typing.List):
        # it will be a dictionary with the key as the word string and the value
        # will be the word's x0,y0,x1,y1 values
        word_coordinates = {}

        # get all words present in pages
        word_list = []
        for page in self._pdf_file.pages():
            # append the values of all pages into one list
            word_list += page.get_text('words')

        # go through all words and see which ones match
        for word in word_list:
            # check list isn't empty, if it is then there is no need to keep looking
            if words:
                # if the word string is in the list
                if word[4] in words:
                    word_coordinates[word[4]] = word[:4]
                    # once word is found, remove it from the list to be found
                    words.remove(word[4])

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

    def _find_rectangles(self, row: dict):
        # data = {'full_name': 'tomas costantino'}
        # to_return = {'full_name': (x0,y0,x1,y1),
        #              'date': (x0,y0,x1,y1)}

        rectangles = {}

        for key, value in row.items():
            words = self._get_words(value)
            locations = self._find_words(words)
            if locations is not None:
                rectangles[key] = self._find_subrectangle(locations)

        return rectangles

    def _mark_rectangles(self, rectangles):
        for page in self._pdf_file.pages():
            for value in rectangles.values():
                r = fitz.Rect(value)  # make rect from word bbox
                page.draw_rect(r, color=[0, 1, 1, 0])  # rectangle
        self._pdf_file.save(self._output_path + '/labelled_' + self._pdf_filename)

    def _match_pdfname_to_row(self):
        pdf_name = self._pdf_filename.split('.')[0]
        return self._rows[int(pdf_name) - 1]

    def _label_document(self):
        row = self._match_pdfname_to_row()
        rectangles = self._find_rectangles(row)
        self._mark_rectangles(rectangles)

    def _create_csv(self):
        pass

    def run(self):
        self._read_csv(input('Insert full path of csv file: '))
        self._input_path = input('Insert full path where the PDF documents are: ')

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
