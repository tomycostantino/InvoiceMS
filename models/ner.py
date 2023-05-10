from __future__ import unicode_literals, print_function
import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding
from spacy.training.example import Example
from tqdm import tqdm
from labeller.ner_labeller import run_ner_labelling


def train_model(model, TRAIN_DATA, n_iter, output_dir):

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
        for ent in annotations['entities']:  # Change this line
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

            print(losses)

    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)


def clean_dataset(dataset):
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
    output_dir = Path('/Users/tomasc/PycharmProjects/IMS/InvoiceMS/models/ner_multi')
    n_iter = 20

    train_model(model, data, n_iter, output_dir)
