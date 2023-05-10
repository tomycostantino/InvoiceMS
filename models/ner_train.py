from __future__ import unicode_literals, print_function
import plac
import random
from pathlib import Path
import spacy
from sklearn.model_selection import train_test_split
from spacy.util import minibatch, compounding
from spacy.training.example import Example
from tqdm import tqdm
from labeller.ner_labeller import run_ner_labelling


def train_model(model, TRAIN_DATA, n_iter, output_dir):
    """
    Training of NER
    :param model:
    :param TRAIN_DATA:
    :param n_iter:
    :param output_dir:
    :return:
    """

    # Split dataset to train and validate to decide best model
    TRAIN_DATA, VALID_DATA = train_test_split(TRAIN_DATA, test_size=0.2)

    # Declare parameters that will hold the current best model
    best_loss = float('inf')
    best_model = None
    best_model_itn = None
    best_model_loss = None

    if model is not None:
        nlp = spacy.load(model)
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank('en')
        print("Created blank 'en' model")

    if 'ner' not in nlp.pipe_names:
        ner = nlp.add_pipe('ner', last=True)
    else:
        ner = nlp.get_pipe('ner')

    for _, annotations in TRAIN_DATA:
        for ent in annotations['entities']:
            ner.add_label(ent[2])

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        examples = []
        for text, annotations in TRAIN_DATA:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            examples.append(example)

        nlp.initialize(lambda: examples)

        for itn in range(n_iter):
            random.shuffle(examples)
            losses = {}

            batches = minibatch(examples, size=compounding(4.0, 32.0, 1.001))
            for batch in tqdm(batches):
                nlp.update(batch, drop=0.5, losses=losses)

            print(f'Iteration n: {itn}')
            print(losses)

            scores = nlp.evaluate(examples)
            total_loss = 1 - scores.get('ents_f', 1)  # Calculate total_loss as 1 - overall F-score

            if total_loss < best_loss:
                best_loss = total_loss
                best_model = nlp
                best_model_itn = itn
                best_model_loss = losses

        nlp = best_model

    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()

        print(f'Saving model of iteration {best_model_itn} with loss of {best_model_loss}')
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)


def clean_dataset(dataset):
    """
    Check the dataset for irregularities and drop them if they exist
    :param dataset:
    :return:
    """

    cleaned_dataset = []
    for data_point in dataset:
        # Check if the data_point is a tuple of length 2
        if not isinstance(data_point, tuple) or len(data_point) != 2:
            print(f"Invalid data point (not a 2-tuple): {data_point}")
            continue

        text, annotations = data_point

        # Check if the text is a string
        if not isinstance(text, str):
            print(f"Invalid data point (text not a string): {data_point}")
            continue

        # Check if annotations is a dictionary with 'entities' key
        if not isinstance(annotations, dict) or 'entities' not in annotations:
            print(f"Invalid data point (annotations not a dict or 'entities' key missing): {data_point}")
            continue

        # Check if 'entities' is a list of tuples of length 3
        if not all(isinstance(ent, tuple) and len(ent) == 3 for ent in annotations['entities']):
            print(f"Invalid data point ('entities' not a list of 3-tuples): {data_point}")
            continue

        # If all checks pass, add the data point to the cleaned dataset
        cleaned_dataset.append(data_point)

    return cleaned_dataset


if __name__ == '__main__':
    data = run_ner_labelling('../invoices')
    data = clean_dataset(data)  # Clean the dataset before using it
    model = None
    output_dir = Path('/Users/tomasc/PycharmProjects/IMS/InvoiceMS/models/ner_multi_1')
    n_iter = 25

    train_model(model, data[:int(len(data)/2)], n_iter, output_dir)
