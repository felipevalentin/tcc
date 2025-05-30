import json
import time
from typing import Dict, List

import ollama
import yaml
import metrics, examples, rag

import config
import utils
from data import experiment
from logger import get_logger

logger = get_logger(__name__)


@utils.backoff(retries=100)
def extract(client, prompts, experiment_config, key, task_id):
    logger.info(f"Task {task_id}: Starting extraction for document {key}")
    start_time = time.perf_counter()

    stream = client.chat(
        model=experiment_config.model,
        messages=prompts,
        format=experiment_config.extraction_model.model_json_schema(),
        options=config.OPTIONS,
        stream=True,
    )

    content_parts: list[str] = []
    for chunk in stream:
        piece = chunk.get("message", {}).get("content")
        if piece:
            content_parts.append(piece)
            print(piece, end="", flush=True)

    full_content = "".join(content_parts)

    extracted_data = experiment_config.extraction_model.model_validate_json(
        full_content, strict=True
    )

    logger.info(
        "Task %s: Finished extraction for document %s in %.2f s",
        task_id,
        key,
        time.perf_counter() - start_time,
    )
    return extracted_data.dict()


def process_prompts(
    experiment_config: experiment.ExperimentConfig, title: str, body: str
) -> List[Dict[str, str]]:
    system = experiment_config.prompt.replace(
        "{SCHEMA}",
        json.dumps(
            experiment_config.extraction_model.model_json_schema(mode="serialization"),
            indent=2,
            ensure_ascii=False,
        ),
    )

    if experiment_config.clean_context:
        body = utils.clean_html_text(body)

    if experiment_config.rag_config is not None:
        body = rag.get_chunks(
            body,
            experiment_config.rag_config.chunk_size,
            experiment_config.rag_config.overlap,
            experiment_config.rag_config.top_k,
        )
        fields = body[1]
        output = ""
        for field, values in fields.items():
            output += f"### {field}\n"
            for value in values:
                output += f"{value}\n"
            output += "\n"
        body = output

    user = f"""# Contexto
## Nome do Documento
{title}

## Texto do Documento
{body}
"""

    example = ""
    if experiment_config.shot == experiment.Shots.ONE_SHOT:
        example = f"{examples.ONE_SHOT}"
    elif experiment_config.shot == experiment.Shots.ONE_SHOT_OUT:
        example = f"{examples.ONE_SHOT_OUT}"
    elif experiment_config.shot == experiment.Shots.FEW_SHOT:
        example = f"{examples.FEW_SHOT}"
    elif experiment_config.shot == experiment.Shots.FEW_SHOT_OUT:
        example = f"{examples.FEW_SHOT_OUT}"
    elif experiment_config.shot == experiment.Shots.DYNAMIC_ONE_SHOT:
        example = f"{examples.dynamic_example(body)}"
    elif experiment_config.shot == experiment.Shots.DYNAMIC_ONE_SHOT_OUT:
        example = f"{examples.dynamic_example_out(body)}"
    elif experiment_config.shot == experiment.Shots.ZERO_SHOT:
        example = ""

    system = system.replace("{EXEMPLO}", example)

    if experiment_config.single_prompt:
        prompts = [
            {"role": "user", "content": system.replace("{CONTEXTO}", user)},
        ]
    else:
        prompts = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    return prompts


def process_documents(client, experiment_config: experiment.ExperimentConfig):
    sample = utils.read_json_to_dict_of_samples()
    logger.info(f"Total documents to process: {len(sample)}")
    results = {}

    for task_id, key in enumerate(sample):
        prompts = process_prompts(
            experiment_config, sample[key].titulo, sample[key].texto
        )
        result = extract(client, prompts, experiment_config, key, task_id)
        if result is not None:
            results[key] = result

    logger.info("All extractions completed.")
    return results


def run():
    logger.info("Starting experiments")

    best_per_field = {}
    scores = {}
    averages = {}
    for file in config.PROMPTS_PATH.iterdir():
        if file.stat().st_size == 0:
            logger.info(f"Skipping empty file: {file}")
            continue

        exp_name = file.stem
        if exp_name not in ["llm"]:
            continue

        with file.open() as f:
            experiments = yaml.safe_load(f)
        client = ollama.Client(host=config.OLLAMA_HOST)
        experiment_configurations = experiment.load_configurations(experiments)
        for exp_config in experiment_configurations:
            output_path = (
                config.RESULTS_PATH / exp_name / "output" / f"{exp_config.id}.json"
            )
            if output_path.exists():
                logger.info(f"Skipping experiment {exp_config.id} because it exists")
                with output_path.open("r") as f:
                    result = json.load(f)
            else:
                result = process_documents(client, exp_config)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with output_path.open("w") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                logger.info(f"Experiment {exp_config.id} completed")

            metrics_path = (
                config.RESULTS_PATH / exp_name / "metrics" / f"{exp_config.id}.json"
            )
            if metrics_path.exists():
                logger.info(
                    f"Skipping metrics generation {exp_config.id} because it exists"
                )
                with metrics_path.open("r") as f:
                    metrics_result = json.load(f)
                # metrics_result = metrics.evaluate_extraction_per_column(
                #     result, utils.read_csv_to_dict_of_ground_truth(), exp_config
                # )
            else:
                metrics_result = metrics.evaluate_extraction_per_column(
                    result, utils.read_csv_to_dict_of_ground_truth(), exp_config
                )
                metrics_path.parent.mkdir(parents=True, exist_ok=True)
                with metrics_path.open("w") as f:
                    json.dump(metrics_result, f, indent=2, ensure_ascii=False)
                logger.info(
                    f"Metrics generation for experiment {exp_config.id} completed"
                )

            def parse_percentage(value: str) -> float:
                return float(value.strip("%"))

            # Initialize
            metric_keys = ["accuracy", "precision", "recall", "f1-score"]
            average_f1 = 0
            for field, metricx in metrics_result.items():
                for metric_key in metric_keys:
                    if metric_key not in metricx:
                        continue  # skip missing metrics

                    try:
                        score = parse_percentage(metricx[metric_key])
                    except ValueError:
                        continue  # skip malformed %

                    if metric_key == "f1-score":
                        average_f1 += score

                    if field not in best_per_field:
                        best_per_field[field] = {}

                    if field not in scores:
                        scores[field] = {}
                    if metric_key not in scores[field]:
                        scores[field][metric_key] = [score]
                    else:
                        scores[field][metric_key].append(score)

                    if (
                        metric_key not in best_per_field[field]
                        or score > best_per_field[field][metric_key]["value"]
                    ):
                        best_per_field[field][metric_key] = {
                            "value": score,
                            "file": f"{exp_config.id}.json",
                            "exp_name": exp_name,
                        }
                    elif (
                        metric_key not in best_per_field[field]
                        or score == best_per_field[field][metric_key]["value"]
                    ):
                        best_per_field[field][metric_key] = {
                            "value": score,
                            "file": f"{exp_config.id}.json + {best_per_field[field][metric_key]['file']}",
                            "exp_name": exp_name
                            + " "
                            + best_per_field[field][metric_key]["exp_name"],
                        }
            averages[exp_config.id] = average_f1 / len(metrics_result)

    print(averages)
    for field in scores:
        print(field, scores[field])

    for field, metricx in best_per_field.items():
        print(f"\nBest scores for field: {field}")
        for metric_name, info in metricx.items():
            print(
                f"  {metric_name}: {info['value']:.2f}% (from {info['file']} experiment {info['exp_name']})",
                end=" ",
            )
        print()
