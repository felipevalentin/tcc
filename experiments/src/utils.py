import csv
import functools
import html
import json
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Union

from bs4 import BeautifulSoup
from pydantic import ValidationError

import logger
from data.models import GroundTruth, Sample

logger = logger.get_logger(__name__)


def read_json_to_dict_of_samples(
    file_path: Path = Path("./resources/ground_truth_data.json"),
) -> Dict[str, Sample]:
    """
    Reads a JSON file and converts it to a dictionary of Sample objects.

    Args:
        file_path: Path to the JSON file.

    Returns:
        A dictionary mapping document codes to Sample objects.
    """
    data = json.loads(file_path.read_text(encoding="utf-8"))
    return {
        item["codigo"]: Sample(**{**item, "texto": html.unescape(item["texto"])})
        for item in data
    }


def read_csv_to_dict_of_ground_truth(
    file_path: Path = Path("./resources/ground_truth_gold_standard.csv"),
) -> Dict[str, GroundTruth]:
    """
    Reads a CSV file and converts it to a dictionary of GroundTruth objects.

    Args:
        file_path: Path to the CSV file.

    Returns:
        A dictionary mapping document codes to GroundTruth objects.
    """
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
    """
    Calculates the number of null values for each field in the samples.

    Args:
        samples: A dictionary of Sample or GroundTruth objects.

    Returns:
        A Counter object with the count of null values per field.
    """
    null_counts = Counter()

    for sample in samples.values():
        for field in sample.model_fields:
            if getattr(sample, field) is None:
                null_counts[field] += 1

    return null_counts


def list_models(client: Any) -> None:
    """
    Lists available models from the client.

    Args:
        client: The client used to list models.
    """
    response = client.list()
    for model in response.models:
        yield model.model, model.details.parameter_size


def clean_html_text(input_text: str) -> str:
    """
    Cleans HTML text by removing tags and normalizing whitespace.

    Args:
        input_text: The input HTML text.

    Returns:
        The cleaned text.
    """
    text_without_html = BeautifulSoup(input_text, "html.parser").get_text()
    text_unescaped = html.unescape(text_without_html)
    text_normalized_x00 = re.sub(r"\x00", "", text_unescaped)
    text_normalized_fffd = re.sub(r"\uFFFD", "", text_normalized_x00)
    text_normalized_new_lines = re.sub(r"\n{2, }", "\n\n", text_normalized_fffd)
    text_normalized_spaces = re.sub(r" +", " ", text_normalized_new_lines)
    return text_normalized_spaces.strip().strip("\n").strip("\r")


def serialize_experiment(
    description: str,
    model: str,
    options: Dict[str, Any],
    metric: Dict[str, Any],
    prompt: str,
    schema: Dict[str, Any],
    extraction_results: Dict[str, Any],
    ground_truth: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Serializes experiment data into a dictionary.

    Args:
        description: Description of the experiment.
        model: Model used for extraction.
        options: Options used for extraction.
        metric: Metrics of the experiment.
        prompt: Prompt used for extraction.
        schema: Schema of the experiment.
        extraction_results: Results of the extraction.
        ground_truth: Ground truth data.

    Returns:
        A dictionary containing serialized experiment data.
    """
    serializable_results = {
        codigo: result.model_dump(mode="json")
        for codigo, result in extraction_results.items()
        if result is not None
    }
    data = {
        "metrics": metric,
        "prompt": prompt,
        "options": options,
        "model": model,
        "schema": schema,
        "serializable": serializable_results,
        "description": description,
        "ground_truth": ground_truth,
    }
    return data


def backoff(delay=2, retries=3, max_delay=64):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except ValidationError as e:
                    return None
                except Exception as e:
                    if attempt == retries:
                        return None
                    logger.warning(
                        f"Attempt {attempt} failed for '{func.__name__}'. "
                        f"Retrying in {current_delay} seconds... Error: {e}"
                    )
                    time.sleep(current_delay)
                    current_delay *= 2
                    if current_delay > max_delay:
                        current_delay = max_delay
            return None

        return wrapper

    return decorator
