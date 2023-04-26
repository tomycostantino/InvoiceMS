import fitz
import csv
import typing
import os
import ast
import math
import bisect
import jellyfish
from data_preprocessing import DataPreProcessing
from dataset_generator.dataset_generator_base import DatasetGeneratorBase
import time


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

        # rows from csv file
        self._rows = []

        # all words from pdf file retrieved with Fitz library
        self._words_in_file = []

        self._pre_processor = DataPreProcessing

    def _read_csv(self, file):
        '''
        will get all rows from the csv that contains the data present in the invoices
        :param file:
        :return:
        '''
        try:
            with open(file, 'r') as f:
                reader = csv.DictReader(f)
                self._rows = [row for row in reader]
                f.close()

            self._rows = self._pre_processor.preprocess_csv_data(self._rows)

        except Exception as e:
            print(e)

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

        self._words_in_file = self._pre_processor.preprocess_pdf_data(self._words_in_file)

    def _get_words_from_pdf(self):
        '''
        Store all words from pdf in the class object
        :return:
        '''

        self._words_in_file = []

        for page in self._current_pdf.pages():
            for idx, word in enumerate(page.get_text('words')):
                w = {
                        'word': word[4],
                        'coordinates': word[:4],
                        'page': page
                    }

                self._words_in_file.append(w)

    def _get_pdf_words_context(self):
        '''
        Given a word, get the context, in this case the shortest distances
        :param words:
        :return:
        '''

        for idx, word in enumerate(self._words_in_file):
            for i, distance in enumerate(self._find_shortest_distances(idx, word, 3)):
                self._words_in_file[idx][f'near_word_{i}'] = distance[0]['word']
                self._words_in_file[idx][f'near_w_{i}_coord'] = distance[0]['coordinates']
                self._words_in_file[idx][f'distance_w_{i}'] = distance[1]

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

    def _calculate_center(self, coord):
        x_center = (coord[0] + coord[2]) / 2
        y_center = (coord[1] + coord[3]) / 2
        return x_center, y_center

    def _calculate_euclidean_distance(self, coord1, coord2):
        '''
        Calculate euclidean distance between two points
        :param w1:
        :param w2:
        :return:
        '''

        center1 = self._calculate_center(coord1)
        center2 = self._calculate_center(coord2)

        return math.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)

    def _calculate_manhattan_distance(self, coord1, coord2):
        '''
        Manhattan distance between two words in document
        :param coord1:
        :param coord2:
        :return:
        '''
        center1 = self._calculate_center(coord1)
        center2 = self._calculate_center(coord2)
        return abs(center1[0] - center2[0]) + abs(center1[1] - center2[1])

    def _find_shortest_distances(self, idx, target, n):
        '''
        Given a word, return the two closest words with the euclidean distance
        :param target:
        :return:
        '''

        sorted_list = []

        # Not going to loop through all words again so calculate the range between 5 and 10 words
        context_start = max(0, idx - 5)
        context_end = min(len(self._words_in_file), idx + 6)

        # Loop through all the words in the pdf
        for near_word in self._words_in_file[context_start:context_end]:
            # only pass the coordinates to calculator
            dist = self._calculate_euclidean_distance(target['coordinates'], near_word['coordinates'])
            # insert into the list and sort it by the value of the dist
            bisect.insort(sorted_list, (near_word, dist), key=lambda x: x[1])

        # don't include the first element as it will be 0 because of being same word
        return sorted_list[1:n + 1]

    def _build_label_dict(self, label: str, word) -> typing.Union[dict, None]:
        '''
        Generates the dict to label a word on the doc
        :param label:
        :param word:
        :return:
        '''

        if word['word'] == '':
            return None

        data = word
        data['label'] = label

        return data

    def _count_word_occurrences(self, target: str) -> typing.List:
        '''
        see if there is more than one target word in page
        :param target:
        :return:
        '''

        occurrences = []
        [occurrences.append(word) for word in self._words_in_file if word.get('word') == target]
        return occurrences

    def _occurrences_in_csv(self, target, csv_fields):
        '''
        Count how many times a target word is repeated across the csv fields
        :param target:
        :param csv_fields:
        :return:
        '''
        occurrences = []

        for occurrence in list(csv_fields.values()):
            for word in occurrence:
                if word == target:
                    occurrences.append(word)

        # if the word is only one time in the csv just return the word dict and not a list with the dicts inside
        return occurrences

    def _find_csv_rectangle(self, rectangles):
        '''
        Calculate the center of the csv field in the pdf and the target word occurrence
        :param rectangles:
        :return:
        '''
        min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')

        for x0, y0, x1, y1 in rectangles:
            min_x = min(min_x, x0)
            min_y = min(min_y, y0)
            max_x = max(max_x, x1)
            max_y = max(max_y, y1)

        return min_x, min_y, max_x, max_y

    def _determine_most_relevant_occurrence(self, full_csv_field_in_pdf, occurrences):
        '''
        Determine the most relevant occurrence by returning the shortest word to a certain rectangle
        :return:
        '''

        closest_distance = float('inf')  # will be compared against to find the actually closest_distance
        closest_occurrence = None  # will be the object of the word that is closest to the csv field

        # loop through all occurrences and measure their distance in respect to the whole csv located in the field
        for occurrence in occurrences:
            occurrence_distance = self._calculate_euclidean_distance(full_csv_field_in_pdf, occurrence['coordinates'])
            if occurrence_distance < closest_distance:
                closest_distance = occurrence_distance
                closest_occurrence = occurrence

        return closest_occurrence

    def _manage_multiple_occurrences(self, occurrences: typing.List, csv_fields):
        '''
        If there is multiple occurrences of one word that is a target, then get the whole column and find the other
        relevant words' coordinates and find the target occurrence with the shortest distance
        :param occurrences:
        :param csv_fields:
        :return:
        '''

        # Count how many times the text of word that is relevant is repeated in the csv
        word_occurrences_in_csv = self._occurrences_in_csv(occurrences[0]['word'], csv_fields)

        # This list will store words that are in the pdf and belong to a certain csv field
        full_csv_field_in_pdf = []

        # If we only have a target word to label in all csv columns, but it is repeated across the pdf, find
        # the most relevant occurrence by measuring the distance between the target and the center of the csv field in
        # the pdf
        if len(word_occurrences_in_csv) == 1:

            # Loop through the words in file to find the ones that belong to a certain csv field
            for word in self._words_in_file:
                # if the text of the word is in the csv and is not one of the target word, then append that word's
                # coordinates to create the rectangle of the full csv field in the pdf doc
                if word['word'] in word_occurrences_in_csv[0] and word['word'] != occurrences[0]['word']:
                    full_csv_field_in_pdf.append(word['coordinates'])

            csv_in_pdf_rectangle = self._find_csv_rectangle(full_csv_field_in_pdf)
            # once we found the csv field in the pdf, calculate the center which will be measured against
            # all relevant occurrences to find the closest one and assign it as relevant
            return [self._determine_most_relevant_occurrence(csv_in_pdf_rectangle, occurrences)]

        else:
            return occurrences

    def _is_relevant(self, target: str, word_list):
        '''
        If a word in the csv is present in the document then it is relevant so return true
        This will be later filtered out to see which one is the most relevant if there is multiple occurrences
        :param target:
        :param word_list:
        :return:
        '''

        for value in list(word_list.values()):
            if target in value:
                return True

        return False

    def _label_pdf_words(self, row_n: int):
        '''
        will put a label to each individual word
        :param page:
        :param row:
        :return:
        '''

        # get a list of the words I want to label
        # individual_words_to_label = self._split_csv_values_into_words(row)
        # csv_fields = [str(val) for val in row.values()]

        label_rows = []

        # Loop through all words in document to find the ones to label
        for word in self._words_in_file:
            # if the word in the pdf matches the one in the csv then it is relevant
            if self._is_relevant(word['word'], self._rows[row_n]):
                # if there is more than one occurence, it must be dealt with
                occurrences = self._count_word_occurrences(word['word'])

                # if it is there only one time then it is relevant and just be labelled as such
                if len(occurrences) == 1:
                    labelled_word = self._build_label_dict('relevant', word)
                    self._draw_rectangle(word, [0, 1, 1, 1])

                else:
                    relevant_occurrences = self._manage_multiple_occurrences(occurrences, self._rows[row_n])
                    labelled_word = self._build_label_dict('relevant' if word in relevant_occurrences else \
                                                           'irrelevant', word)
                    self._draw_rectangle(word, [0, 1, 1, 1]) if word in relevant_occurrences else self._draw_rectangle(
                        word)

            else:
                labelled_word = self._build_label_dict('irrelevant', word)
                self._draw_rectangle(word)

            if labelled_word is not None:
                label_rows.append(labelled_word)
            else:
                continue

        self._current_pdf.close()

        return label_rows

    def _draw_rectangle(self, word, color=[0, 1, 1, 0]):
        try:
            word['page'].draw_rect(word['coordinates'], color)
            self._current_pdf.save(self._pdf_output_path + '/labelled_' + self._current_pdf_filename)

        except ValueError:
            print('couldnt print')
        # once document is finished, clear list

    def _match_pdfname_to_row(self):
        '''
        pdf filename must be the pdf number so it matches the row
        :return:
        '''

        pdf_name = self._current_pdf_filename.split('.')[0]
        return int(pdf_name) - 1

    def _label_document(self):
        '''
        Will label doc by doc
        :return:
        '''

        row = self._match_pdfname_to_row()  # if we are reading '80.pdf', then retrieve data from 80th row
        return self._label_pdf_words(row)

    def _build_dataset(self, filename, labels):
        '''
        Create csv file with all documents labels
        :param labels:
        :return:
        '''

        with open(filename, mode='w', newline='') as file:
            fieldnames = None

            # make the fieldnames, thing is to remove the page object because it will make the code crash
            # just need to go through one of them that is the break for
            for pdf_label_list in labels:
                for data_dict in pdf_label_list:
                    fieldnames = list(data_dict.keys())
                    fieldnames.remove('page')
                    break
                break

            # now write header
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            # write all fields now
            for pdf_label_list in labels:
                for data_dict in pdf_label_list:
                    data_dict.pop('page')
                    writer.writerow(data_dict)

        print(f"Data has been successfully written to {filename}")

    def run(self, invoices_folder):
        '''
        Run the labelling process on each folder of invoice template
        :return:
        '''

        # check if folder has already been labelled
        already_labelled_folder = []
        for already_existing_dataset in os.listdir('../datasets'):
            if already_existing_dataset.startswith('invoice'):
                already_labelled_folder.append(already_existing_dataset.split('.')[0])

        for folder in os.listdir(invoices_folder):
            if folder.startswith('invoice') and folder not in already_labelled_folder:

                print(f'Labelling {folder} folder')

                # Read data to label pdfs
                self._read_csv(f'{invoices_folder}/{folder}/data.csv')
                self._pdf_input_path = f'{invoices_folder}/{folder}/generated_pdf'

                # create path for labelled pdfs
                directory_name = self._pdf_input_path.split('/')[-1]
                self._pdf_output_path = self._pdf_input_path.replace(directory_name, 'labelled_pdf')
                os.makedirs(self._pdf_output_path, exist_ok=True)

                # find path of invoice template number
                csv_output = self._pdf_input_path.split('/')[-2]

                dataset = []

                # run through all files in the directory
                for file in os.listdir(self._pdf_input_path):
                    if file.endswith('.pdf'):

                        # start clock to calculate time taken per document
                        start_time = time.time()

                        # make the class change pdfs as we loop through the directory files
                        self._read_pdf(file)

                        # go through the labelling pipeline
                        dataset.append(self._label_document())

                        # stop clock and print out time taken
                        end_time = time.time()
                        print(f'Time taken to label {file} was {round(end_time - start_time, 5)} seconds')

                self._build_dataset(f'../datasets/{csv_output}.csv', dataset)

            else:
                print(f'{folder} already labelled')


def main():
    lab = DataLabeller()
    lab.run('../invoices')


if __name__ == '__main__':
    main()
