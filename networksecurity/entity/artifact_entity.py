from dataclasses import dataclass


@dataclass
class DataIngestionArtifact:
    # Path where the training dataset will be stored
    training_file_path: str

    # Path where the testing dataset will be stored
    test_file_path: str