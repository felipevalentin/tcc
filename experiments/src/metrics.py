import re
from enum import Enum
from typing import Union, get_args, get_origin

import Levenshtein
import unidecode
from data.experiment import ExperimentConfig
from logger import get_logger

logger = get_logger(__name__)


def _unwrap_enum(annotation):
    """
    Returns the Enum subclass contained in an annotation.

    Handles:
    * plain Enum: MyEnum
    * Optional[MyEnum]
    * Union[MyEnum, None]
    """
    origin = get_origin(annotation)
    if origin is Union:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) == 1 and isinstance(args[0], type) and issubclass(args[0], Enum):
            return args[0]
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return annotation
    return None


def evaluate_extraction_per_column(
    extraction_results, ground_truth, experiment_configuration: ExperimentConfig
):
    model = experiment_configuration.extraction_model
    fields = [f for f in model.model_fields if f != "raciocínio"]
    # Detect enum‑typed fields so we can treat them as multi‑class tasks
    enum_fields = {}
    # Detect enum‑typed fields (including Optional[...] enums) and add `None`
    enum_fields = {}
    for f in fields:
        enum_type = _unwrap_enum(model.model_fields[f].annotation)
        if enum_type:
            enum_fields[f] = list(enum_type)
    counters = {}
    for f in fields:
        if f in enum_fields:
            # One confusion‑count dict per class label
            counters[f] = {
                label: {"tp": 0, "fp": 0, "fn": 0} for label in enum_fields[f]
            }
            counters[f]["correct"] = 0
        else:
            counters[f] = {
                "correct": 0,
                "true_positive": 0,
                "predicted_positive": 0,
                "nulls": 0,
            }
    total = len(ground_truth)

    for codigo, truth in ground_truth.items():
        try:
            pred = extraction_results[codigo]
        except KeyError as e:
            logger.info(f"Task {codigo}: KeyError: {e}")
            pred = {}
        truth_dump = truth.model_dump()

        logger.info(f"\n\nEvaluating document {codigo}...")
        for field in fields:
            pred_val = pred.get(field)
            true_val = truth_dump.get(field)

            # ----- ENUM FIELDS: multi-class accounting (NULL is ignored) -----
            if field in enum_fields:
                if pred_val == true_val:
                    counters[field]["correct"] += 1

                if pred_val == true_val and true_val is not None:
                    counters[field][true_val]["tp"] += 1
                else:
                    if pred_val is not None:
                        logger.info(
                            f"Field '{field}' is incorrect\nExpected: <{true_val}>\nGot: <{pred_val}>"
                        )
                        counters[field][pred_val]["fp"] += 1
                    if true_val is not None:
                        counters[field][true_val]["fn"] += 1
                continue

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
                    single_spaced = re.sub(r" {2,}", " ", kept).strip().strip("0")
                    return single_spaced.casefold()
                return val

            n_pred = normalize(pred_val) if pred_val else pred_val
            n_true = normalize(true_val) if true_val else true_val

            if field == "objeto" and pred_val and true_val:
                similarity = Levenshtein.ratio(n_pred, n_true)
                logger.info(f"Levenshtein distance for field '{field}': {similarity}")
                if similarity > 0.8:
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
    logger.info(f"\n\n")
    for field in fields:
        if field in enum_fields:
            field_metrics = {}
            macro_precisions = []
            macro_recalls = []

            for label, c in counters[field].items():
                if label == "correct":
                    continue

                tp = c["tp"]
                fp = c["fp"]
                fn = c["fn"]
                support = tp + fn  # how many ground‑truth instances of this label

                precision = tp / (tp + fp) if (tp + fp) else 0
                recall = tp / support if support else 0

                field_metrics[str(label)] = {
                    "precision": precision,
                    "recall": recall,
                    "support": support,
                }

                # Only include labels that actually appear in the sample
                if support:
                    macro_precisions.append(precision)
                    macro_recalls.append(recall)

            # Compute macro‑average metrics for this enum field (only labels with support)
            macro_precision = (
                sum(macro_precisions) / len(macro_precisions) if macro_precisions else 0
            )
            macro_recall = (
                sum(macro_recalls) / len(macro_recalls) if macro_recalls else 0
            )
            macro_f1 = (
                2 * macro_precision * macro_recall / (macro_precision + macro_recall)
                if macro_precision + macro_recall
                else 0
            )
            # Compute overall accuracy for this enum field
            accuracy = counters[field]["correct"] / total

            field_metrics["__macro__"] = {
                "type": "macro",
                "precision": f"{macro_precision:.2%}",
                "recall": f"{macro_recall:.2%}",
                "f1-score": f"{macro_f1:.2%}",
                "accuracy": f"{accuracy:.2%}",
            }

            logger.info(
                f"{field}::macro (support>0): precision {macro_precision:.2%} "
                f"recall {macro_recall:.2%} f1-score {macro_f1:.2%} "
                f"accuracy {accuracy:.2%}"
            )

            metrics[field] = field_metrics["__macro__"]
            continue

        # ---------- NON‑ENUM FIELDS ----------
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
            "type": "non-macro",
            "accuracy": f"{accuracy:.2%}",
            "recall": f"{recall:.2%}",
            "precision": f"{precision:.2%}",
            "f1-score": f"{f1_score:.2%}",
        }

        logger.info(
            f"{field}: accuracy {accuracy:.2%} recall {recall:.2%} "
            f"precision {precision:.2%} f1-score {f1_score:.2%}"
        )

    # Log null counts (non‑enum fields only)
    logger.info(
        "Null counts (non‑enum fields only): "
        + " ".join(
            f"{f}: {counters[f]['nulls']}" for f in fields if f not in enum_fields
        )
    )

    return metrics
