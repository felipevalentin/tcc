import re

import Levenshtein
import unidecode

from src.models import models
from logger import get_logger

logger = get_logger(__name__)


def evaluate_extraction_per_column(extraction_results, ground_truth):
    fields = [f for f in models.Licitação.model_fields if f != "raciocínio"]
    counters = {
        f: {"correct": 0, "true_positive": 0, "predicted_positive": 0, "nulls": 0}
        for f in fields
    }
    total = len(ground_truth)

    for codigo, truth in ground_truth.items():
        try:
            pred = extraction_results[codigo].model_dump()
            truth_dump = truth.model_dump()
        except KeyError as e:
            logger.info(f"Task {codigo}: KeyError: {e}")
            continue

        logger.info(f"\n\nEvaluating document {codigo}...")
        for field in fields:
            pred_val = pred.get(field)
            true_val = truth_dump.get(field)

            if true_val is None:
                counters[field]["nulls"] += 1
            if pred_val is not None:
                counters[field]["predicted_positive"] += 1

            if pred_val is None and true_val is None:
                counters[field]["correct"] += 1
                continue

            if field == "data_de_abertura":
                match = (
                    pred_val
                    and true_val
                    and pred_val == true_val.strftime("%Y-%m-%dT%H:%M")
                )
                if match:
                    counters[field]["correct"] += 1
                    counters[field]["true_positive"] += 1
                else:
                    logger.info(
                        f"Field '{field}' is incorrect\nExpected: {true_val}\nGot: {pred_val}"
                    )
                continue

            def normalize(val):
                if isinstance(val, str):
                    ascii_str = unidecode.unidecode(val)
                    kept = re.sub(r"[^A-Za-z0-9 /]+", "", ascii_str)
                    single_spaced = re.sub(r" {2,}", " ", kept).strip()
                    return single_spaced.casefold()
                return val

            n_pred = normalize(pred_val) if pred_val else pred_val
            n_true = normalize(true_val) if true_val else true_val

            if field == "objeto" and pred_val and true_val:
                similarity = Levenshtein.ratio(n_pred, n_true)
                logger.info(f"Levenshtein distance for field '{field}': {similarity}")
                if similarity > 0.9:
                    counters[field]["correct"] += 1
                    counters[field]["true_positive"] += 1
                else:
                    logger.info(
                        f"Field '{field}' is incorrect\nExpected: <{true_val}>\nGot: <{pred_val}>"
                    )
                continue

            if n_pred == n_true:
                counters[field]["correct"] += 1
                counters[field]["true_positive"] += 1
            else:
                logger.info(
                    f"Field '{field}' is incorrect - Expected: {true_val}, Got: {pred_val}"
                )

    metrics = {}
    for field in fields:
        correct = counters[field]["correct"]
        tp = counters[field]["true_positive"]
        pred_pos = counters[field]["predicted_positive"]
        actual_pos = total - counters[field]["nulls"]

        accuracy = correct / total if total else 0
        recall = tp / actual_pos if actual_pos else 0
        precision = tp / pred_pos if pred_pos else 0
        f1_score = (
            2 * precision * recall / (precision + recall) if precision + recall else 0
        )

        metrics[field] = {
            "accuracy": accuracy,
            "recall": recall,
            "precision": precision,
            "f1-score": f1_score,
        }

        logger.info(
            f"{field}: accuracy {accuracy:.2%} recall {recall:.2%} precision {precision:.2%} f1-score {f1_score:.2%}"
        )

    # Log null counts
    logger.info(
        "Null counts: " + " ".join(f"{f}: {counters[f]['nulls']}" for f in fields)
    )

    return metrics
