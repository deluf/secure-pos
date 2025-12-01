import csv
from dataclasses import asdict
from sklearn.model_selection import train_test_split

from segregation_system.prepared_sessions_db import PreparedSession

class DataSplitter:
    def __init__(
        self,
        train_split_percentage: float,
        validation_split_percentage: float,
        test_split_percentage: float
    ):
        self.train_split_percentage = train_split_percentage
        self.validation_split_percentage = validation_split_percentage
        self.test_split_percentage = test_split_percentage

    def split(self, sessions: list[PreparedSession]):
        print("Starting data split process using sklearn...")

        # First Split: Separate Train from the rest (Validation + Test)
        train_set, temp_set = train_test_split(
            sessions,
            train_size=self.train_split_percentage,
            shuffle=True
        )

        # Second Split: Separate Validation and Test from the 'temp_set'
        # We must recalculate the split ratio relative to the remaining data.
        relative_test_size = self.test_split_percentage / (self.validation_split_percentage + self.test_split_percentage)
        val_set, test_set = train_test_split(
            temp_set,
            test_size=relative_test_size,
            shuffle=True
        )

        self._save_to_csv("train_set.csv", train_set)
        self._save_to_csv("validation_set.csv", val_set)
        self._save_to_csv("test_set.csv", test_set)

        print("Data splitting complete.")

    def _save_to_csv(self, filename, data):
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                # Extract headers dynamically from the first item in the list
                headers = asdict(data[0]).keys()
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for item in data:
                    writer.writerow(asdict(item))
            print(f"Saved {len(data)} records to {filename}")
        except Exception as e:
            print(f"Error saving {filename}: {e}")
