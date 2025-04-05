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
    # gemma3:12b 12.2B
    # gemma3:4b 4.3B
    # gemma3:1b 999.89M
    # gemma3:27b-it-fp16 27.4B
    # qwen2.5:72b-instruct 72.7B
    # deepseek-r1:32b-qwen-distill-q4_K_M 32.8B
    # deepseek-r1:70b 70.6B
    # qwen2.5:0.5b 494.03M
    # qwen2.5:1.5b 1.5B
    # llama3.3:70b 70.6B
    # llama3.3:latest 70.6B
    # llama3.2-vision:latest 9.8B
    # llama3.2:longe-ctx 3.2B
    # qwen2.5:latest 7.6B
    # nomic-embed-text:latest 137M
    # qwen2.5-coder:32b 32.8B
    # llama3.2:1b 1.2B
    # mistral-nemo:12b-instruct-2407-fp16 12.2B
    # nemotron:70b-instruct-q8_0 70.6B
    # llama3.2:3b 3.2B
    # llama3.2:latest 3.2B
    # mistral-large:123b 122.6B
    # qwen2.5:72b 72.7B
    # llama3.1:70b 70.6B
    # qwen2.5:32b-instruct 32.8B
    # qwen2.5:72b-instruct-q4_0 72.7B
    # llama2-uncensored:latest 7B
    # qwen2.5:7b 7.6B
    # qwen2.5:3b 3.1B
    response = client.list()
    for model in response.models:
        print(model.model, model.details.parameter_size)
