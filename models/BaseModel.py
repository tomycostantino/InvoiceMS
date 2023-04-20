# Tomas Costantino - A00042881

import glob
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from collections import defaultdict
from tensorflow import keras
from tensorflow.keras import layers


class BaseModel:
    def __init__(self, data_folders):
        '''
        Set general parameters
        '''
        self._IMG_SIZE = (94, 125)  # size that all images will be resized to
        self._SAMPLE_SIZE = 2048    # size of training sample
        self._valid_size = 512      # size of validation sample
        self._fc_size = 512         # DN yet
        self._model = None          # General model the inheriting classes will call
        self._history = None        # DN yet

        self._x_train, self._labels_train, self._x_valid, self._labels_valid = self.preprocess_data(data_folders)

    def pixels_from_path(self, file_path):
        '''
        Open image file, resize, and return it as a np array with the pixel values
        :param file_path:
        :return:
        '''
        im = Image.open(file_path)

        im = im.resize(self._IMG_SIZE)
        # matrix of pixel RGB values
        return np.array(im)

    def count_shapes(self, folder):
        '''
        loop through the images in the folder (limited to the first 1000 images in this case), and counts the number of
        images with each unique shape (i.e., the dimensions of the image in pixels).
        :param folder:
        :return:
        '''
        shape_counts = defaultdict(int)
        for i, obj in enumerate(glob.glob(f'{folder}/*')[:1000]):
            if i % 100 == 0:
                print(i)
            img_shape = self.pixels_from_path(obj).shape
            shape_counts[str(img_shape)] = shape_counts[str(img_shape)] + 1

        return shape_counts

    def load_train_sample(self, folder):
        '''
        load training dataset from folder, use first 80% of files
        :param folder:
        :return:
        '''
        print(f"loading training {folder} images...")
        return np.asarray([self.pixels_from_path(obj) for obj in glob.glob(f'{folder}/*')[:self._SAMPLE_SIZE]])

    def load_validation_sample(self, folder):
        '''
        load validation dataset from folder, use the last 20% of files
        :param folder:
        :return:
        '''
        print(f"loading validation {folder} images...")
        return np.asarray([self.pixels_from_path(obj) for obj in glob.glob(f'{folder}/*')[-self._valid_size:]])

    def build_training_dataset(self, sets):
        '''
        concatenate multiple datasets of different classes to create one only training dataset
        :param sets: the sets are a list of individual folders with images
        :return:
        '''
        x_train = np.concatenate(sets)
        labels_train = np.asarray([1 for _ in range(self._SAMPLE_SIZE)] + [0 for _ in range(self._SAMPLE_SIZE)])

        return x_train, labels_train

    def build_validation_dataset(self, sets):
        '''
        concatenate multiple datasets of the correspondent classes for validation
        :param sets:
        :return:
        '''
        x_valid = np.concatenate(sets)
        labels_valid = np.asarray([1 for _ in range(self._valid_size)] + [0 for _ in range(self._valid_size)])

        return x_valid, labels_valid

    def vectorise_images(self):
        '''
        turn images into vectors for the model to predict
        :return:
        '''
        inputs = keras.Input(shape=(self._IMG_SIZE[1], self._IMG_SIZE[0], 3), name='ani_image')
        x = layers.Flatten(name='flattened_img')(inputs)  # turn image to vector.

        x = layers.Dense(self._fc_size, activation='relu', name='first_layer')(x)
        outputs = layers.Dense(1, activation='sigmoid', name='class')(x)

        return inputs, outputs

    def preprocess_data(self, folders):
        '''
        Prepare data for parent class to train model quicker
        :param train_folders:
        :param valid_folders:
        :return:
        '''
        train_sets = []
        valid_sets = []

        for data in folders:
            train_sets.append(self.load_train_sample(data))
            valid_sets.append(self.load_validation_sample(data))

        x_train, labels_train = self.build_training_dataset(train_sets)
        x_valid, labels_valid = self.build_validation_dataset(valid_sets)

        return x_train, labels_train, x_valid, labels_valid

    def evaluate(self):
        '''
        Evaluation of inheriting models
        :return:
        '''
        # Check if the model has been created
        if self._model is not None:
            # Make predictions on the validation data
            preds = self._model.predict(self._x_valid)

            # Convert predictions to a NumPy array
            preds = np.asarray([pred[0] for pred in preds])

            # Calculate and print the correlation coefficient between predictions and validation labels
            print('Correlation coefficient between predictions and validation labels: \n',
                  np.corrcoef(preds, self._labels_valid))

            # Calculate and print model performance for various thresholds
            for i in range(1, 10):
                threshold = 0.1 * i
                print(f'threshold: {threshold}')
                accuracy = sum(self._labels_valid[preds > threshold]) / self._labels_valid[preds > threshold].shape[0]
                print(f'Accuracy for threshold {threshold}: {accuracy}')

            # Print the mean of all predictions, and the mean for each class in the validation labels
            print(f'Mean of all predictions: {preds.mean()}')
            print(f'Mean of predictions for class 0 (validation labels): {preds[self._labels_valid == 0].mean()}')
            print(f'Mean of predictions for class 1 (validation labels): {preds[self._labels_valid == 1].mean()}')

            # Create a scatter plot of predictions against validation labels using Seaborn
            sns.scatterplot(x=preds, y=self._labels_valid)
            plt.show()

        else:
            # If the model has not been created, print a warning message
            print('Model has not been constructed yet')

    def save_model(self, name):
        '''
        Once model trained, save it to reuse it without needing to train again
        :param name:
        :return:
        '''
        self._model.save(name)


if __name__ == '__main__':
    model = BaseModel(['cats', 'dogs'])
