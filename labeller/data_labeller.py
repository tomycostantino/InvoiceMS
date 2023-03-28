import fitz
import csv
import typing


class DataLabeller:
    def __init__(self):
        pass

    def _read_csv(self, file):
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            return [row for row in reader]

    def _find_x0(self, values):
        return min(values)

    def _find_y0(self, values):
        return min(values)

    def _find_x1(self, values):
        return max(values)

    def _find_y1(self, values):
        return max(values)

    def _get_words(self, value: str):
        return [v for v in value.split(' ')]

    def _find_words(self, file, words: typing.List):
        # it will be a dictionary with the key as the word string and the value
        # will be the word's x0,y0,x1,y1 values
        words_coordinates = {}

        # get all words present in pages
        word_list = []
        for page in file.pages():
            word_list.append(page.get_text('words'))

        # go through all words and see which ones match
        for word in word_list[0]:
            # check list isn't empty, if it is then there is no need to keep looking
            if words:
                # if the word string is in the list
                if word[4] in words:
                    words_coordinates[word[4]] = word[:4]
                    words.remove(word[4])

            # when found all words bail out
            else:
                break

        return words_coordinates

    def _find_subrectangle(self, locations):
        for key, value in locations.items():
            # need to work on this
            x0s = [x0 for x0 in locations[0]]
            y0s = [y0 for y0 in locations[1]]
            x1s = [x1 for x1 in locations[0]]
            y1s = [y1 for y1 in locations[0]]

        subrectangle = (self._find_x0(x0s), self._find_y0(y0s),
                        self._find_x1(x1s), self._find_y1(y1s))

        return subrectangle

    def find_rectangles(self, file, data: dict):
        # data = {'full_name': 'tomas costantino'}
        # to_return = {'full_name': {'tomas costantino': (x0,y0,x1,y1)}}

        for key, value in data.items():
            words = self._get_words(value)
            locations = self._find_words(file, words)
            print(self._find_subrectangle(locations.values()))

    def _mark_rectangle(self):
        pass

    def label_document(self, file):
        pass


def main():
    rows = {1: 'Rios-Hayes',
            2: '2792 Davis Freeway Williamsberg, NE 69282',
            3: '(602)772-1036x2633',
            4: '20185133',
            5: '08 November, 2019',
            6: 'Fuentes Harris',
            }

    lab = DataLabeller()
    doc = fitz.open('template.pdf')
    lab.find_rectangles(doc, rows)


if __name__ == '__main__':
    main()
