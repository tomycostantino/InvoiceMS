import fitz


class PDFDataReader:
    def __init__(self):
        pass

    def retrieve_data(self, filename):
        '''
        Read data for when model is used in production
        :param filename:
        :return:
        '''

        pdf = fitz.open(filename)
        words_in_file = []
        for page in pdf.pages():
            for word in page.get_text('words'):
                words_in_file.append(
                    {
                        'word': word[4],
                        'coordinates': self._round_coordinates(word[:4]),
                    }
                )
        return words_in_file

    def _round_coordinates(self, coordinates):
        '''
        Round coordinates to 4 decimal points and return as tuple
        :param coordinates:
        :return:
        '''
        rounded_coordinates = []
        for coordinate in coordinates:
            rounded_coordinates.append(round(coordinate, 4))

        return tuple(rounded_coordinates)
