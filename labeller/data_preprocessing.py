import re
from typing import List, Dict


class DataPreProcessing:

    @staticmethod
    def preprocess_pdf_word(word: str) -> str:
        '''
        :param word:
        :return:
        '''
        word = word.lower()
        word = re.sub(r'\W+', '', word)
        return word

    @staticmethod
    def preprocess_pdf_data(words_in_file: List[Dict]) -> List[Dict]:
        '''

        :param words_in_file:
        :return:
        '''
        preprocessed_data = []
        for word_data in words_in_file:
            for key, value in word_data.items():
                # just preprocess the word strings, not all other values
                if key.__contains__('word'):
                    word_data[key] = DataPreProcessing.preprocess_pdf_word(value)
            preprocessed_data.append(word_data)
        return preprocessed_data

    @staticmethod
    def preprocess_csv_data(rows: List[Dict]) -> List[Dict]:
        '''
        :param rows:
        :return:
        '''

        preprocessed_data = []
        for row in rows:
            preprocessed_row = {}
            for key, value in row.items():
                if isinstance(value, str):
                    preprocessed_value = [
                        DataPreProcessing.preprocess_pdf_word(word)
                        for word in value.split()
                    ]
                    preprocessed_row[key] = preprocessed_value
                else:
                    preprocessed_row[key] = value
            preprocessed_data.append(preprocessed_row)
        return preprocessed_data


if __name__ == '__main__':
    pp = DataPreProcessing()
