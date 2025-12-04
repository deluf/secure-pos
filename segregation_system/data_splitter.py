"""
Module for splitting a dataset of prepared sessions into training, validation, and test subsets
"""

import csv
import os
import uuid
from dataclasses import fields, astuple
from pathlib import Path

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
        test_split_percentage: float,
        output_dir: str
    ) -> None:
        self.train_split_percentage = train_split_percentage
        self.validation_split_percentage = validation_split_percentage
        self.test_split_percentage = test_split_percentage
        self.output_dir = output_dir

    def split(self, sessions: list[PreparedSession]) -> list[str]:
        """
        Splits a list of prepared sessions into training, validation, and test sets.
        The splits are then saved into separate CSV files
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
        validation_set, test_set = train_test_split(
            temp_set,
            test_size=relative_test_size,
            shuffle=True
        )

        output_files = []
        splits_id = uuid.uuid4() # Avoids overwriting previous splits
        os.makedirs(self.output_dir, exist_ok=True)
        for split_name, split_data in zip(
                ["train", "validation", "test"], [train_set, validation_set, test_set]):
            path = f"{self.output_dir}/{split_name}_set.{splits_id}.csv"
            self._save_to_csv(path, split_data)
            output_files.append(path)
        return output_files

    @staticmethod
    def delete(paths: list[str]) -> None:
        """
        Deletes the specified files from the filesystem
        """
        for path in paths:
            Path(path).unlink(missing_ok=True)
            print(f"[DataSplitter] Deleted '{path}'")

    @staticmethod
    def _save_to_csv(path: str, data: list[PreparedSession]) -> None:
        """
        Saves a list of prepared sessions to a CSV file
        """
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Write headers based on the Dataclass fields
            writer.writerow([field.name for field in fields(PreparedSession)])
            writer.writerows(astuple(item) for item in data)
        print(f"[DataSplitter] Saved {len(data)} sessions to '{path}'")
