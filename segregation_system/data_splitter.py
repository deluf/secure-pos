"""
Module for splitting a dataset of prepared sessions into training, validation, and test subsets
"""

import csv
from dataclasses import fields, astuple
from sklearn.model_selection import train_test_split

from segregation_system.prepared_sessions_db import PreparedSession

class DataSplitter:
    """
    Splits a dataset of prepared sessions into training, validation,
     and test subsets based on user-defined percentage splits

    :ivar train_split_percentage: Percentage of the dataset to be used for training [0, 1]
    :type train_split_percentage: float
    :ivar validation_split_percentage: Percentage of the dataset to be used for validation [0, 1]
    :type validation_split_percentage: float
    :ivar test_split_percentage: Percentage of the dataset to be used for testing [0, 1]
    :type test_split_percentage: float
    """
    def __init__(
        self,
        train_split_percentage: float,
        validation_split_percentage: float,
        test_split_percentage: float
    ):
        """
        Initializes the class attributes

        :param train_split_percentage:  Percentage of the dataset to be used for training [0, 1]
        :type train_split_percentage: float
        :param validation_split_percentage: Percentage of the dataset to be used for validation [0, 1]
        :type validation_split_percentage: float
        :param test_split_percentage: Percentage of the dataset to be used for testing [0, 1]
        :type test_split_percentage: float
        """
        self.train_split_percentage = train_split_percentage
        self.validation_split_percentage = validation_split_percentage
        self.test_split_percentage = test_split_percentage

    def split(self, sessions: list[PreparedSession]) -> None:
        """
        Splits a list of prepared sessions into training, validation, and test sets.
        The splits are then saved to separate CSV files

        :param sessions: The list of prepared sessions that need to be split
        :type sessions: list[PreparedSession]
        :return: None
        """
        # First Split: Separate Train from the rest (Validation + Test)
        train_set, temp_set = train_test_split(
            sessions,
            train_size=self.train_split_percentage,
            shuffle=True
        )

        # Second Split: Separate Validation and Test from the 'temp_set'
        # We must recalculate the split ratio relative to the remaining data
        relative_test_size = (self.test_split_percentage /
            (self.validation_split_percentage + self.test_split_percentage))
        val_set, test_set = train_test_split(
            temp_set,
            test_size=relative_test_size,
            shuffle=True
        )

        self._save_to_csv("output/train_set.csv", train_set)
        self._save_to_csv("output/validation_set.csv", val_set)
        self._save_to_csv("output/test_set.csv", test_set)

    @staticmethod
    def _save_to_csv(filename: str, data: list[PreparedSession]) -> None:
        """
        Saves a list of prepared sessions to a CSV file

        :param filename: The name of the CSV file where data will be saved
        :type filename: str
        :param data: A list of prepared sessions
        :type data: List[PreparedSession]
        :return: None
        """
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Write headers based on the Dataclass fields
            writer.writerow([field.name for field in fields(PreparedSession)])
            writer.writerows(astuple(item) for item in data)
        print(f"[DataSplitter] Saved {len(data)} records to '{filename}'")
