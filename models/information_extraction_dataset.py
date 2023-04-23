import torch
import pandas as pd
from torch.utils.data import Dataset


class InformationExtractionDataset(Dataset):
    """
    Custom PyTorch Dataset class for the Information Extraction task.

    This class tokenizes and processes the input data using the provided tokenizer
    and max_length. It is designed to be used with Hugging Face Transformers library.

    Args:
        data (pd.DataFrame): The input data as a pandas DataFrame.
        tokenizer (transformers.PreTrainedTokenizer): The tokenizer to use for preprocessing the text data.
        max_length (int): The maximum length of the tokenized sequences.
    """

    def __init__(self, data, tokenizer, max_length):
        self.tokenizer = tokenizer
        self.data = pd.DataFrame(data)
        self.max_length = max_length

    def __len__(self):
        """
        Returns the number of samples in the dataset.
        """
        return len(self.data)

    def __getitem__(self, idx):
        """
        Returns a single preprocessed sample from the dataset at the specified index.

        Args:
            idx (int): The index of the sample to fetch.

        Returns:
            dict: A dictionary containing the preprocessed input_ids, attention_mask, and label.
        """
        row = self.data.iloc[idx]
        text = row["word_coordinates"]
        label = 1 if row["label"] == "relevant" else 0

        # Tokenize the text and prepare the inputs for the transformer model
        inputs = self.tokenizer.encode_plus(
            text,
            None,
            add_special_tokens=True,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_token_type_ids=True,
            return_attention_mask=True,
            return_tensors="pt",
        )

        return {
            "input_ids": inputs["input_ids"].flatten(),
            "attention_mask": inputs["attention_mask"].flatten(),
            "labels": torch.tensor(label, dtype=torch.long),
        }
