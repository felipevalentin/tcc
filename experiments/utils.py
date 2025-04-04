from pathlib import Path
import json
import csv
from collections import Counter
from typing import Dict, Union
from models import Sample, GroundTruth


def read_json_to_dict_of_samples(
    file_path: Path = Path("../resources/sample.json"),
) -> Dict[str, Sample]:
    data = json.loads(file_path.read_text(encoding="utf-8"))
    return {item["codigo"]: Sample(**item) for item in data}


def read_csv_to_dict_of_ground_truth(
    file_path: Path = Path("../resources/ground_truth.csv"),
) -> Dict[str, GroundTruth]:
    ground_truths = {}
    with file_path.open(mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            cleaned_row = {
                key: (None if value == "NULL" else value) for key, value in row.items()
            }
            ground_truth = GroundTruth(**cleaned_row)
            ground_truths[ground_truth.codigo] = ground_truth
    return ground_truths


def calculate_null_values(samples: Dict[str, Union[Sample, GroundTruth]]) -> Counter:
    null_counts = Counter()

    for sample in samples.values():
        for field in sample.model_fields:
            if getattr(sample, field) is None:
                null_counts[field] += 1

    return null_counts


def list_models(client):
    # client = ollama.Client(host="https://ollama-dev.ceos.ufsc.br/")
    response = client.list()
    for model in response.models:
        print(model.model, model.details.parameter_size)
