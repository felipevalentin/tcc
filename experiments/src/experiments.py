import time

import ollama
from pydantic import ValidationError

import examples
import models
import repository
import utils
from config import MAX_RETRIES, MODEL_NAME, OLLAMA_HOST, OPTIONS, PROMPT
from logger import get_logger
from metrics import evaluate_extraction_per_column
from repository import get_connection, init_db

logger = get_logger(__name__)


def extract(client, task_id, codigo, context, prompt):
    prompt = (
        prompt.replace("{EXEMPLO_1}", examples.EXAMPLE_1).replace(
            "{EXEMPLO_1_OUTPUT}", examples.EXAMPLE_1_OUTPUT
        ).replace("{EXEMPLO_2}", examples.EXAMPLE_2).replace(
            "{EXEMPLO_2_OUTPUT}", examples.EXAMPLE_2_OUTPUT
        )
    )
    for attempt in range(1, MAX_RETRIES + 1):
        logger.info(
            f"Task {task_id}: Starting extraction for document {codigo} (Attempt {attempt})"
        )
        try:
            start_time = time.perf_counter()
            response = client.chat(
                model=MODEL_NAME,
                messages=[
                    # {
                    #     "role": "system",
                    #     "content": prompt
                    # },
                    {"role": "user", "content": f"{prompt}\n**CONTEXTO**\n{context}"},
                ],
                format=models.Licitação.model_json_schema(),
                options=OPTIONS,
            )
            content = response["message"]["content"]
            extracted_data = models.Licitação.model_validate_json(content, strict=True)
            logger.info(
                f"Task {task_id}: Finished extraction for document {codigo} in {time.perf_counter() - start_time:.2f} seconds"
            )
            return extracted_data
        except ValidationError as e:
            logger.info(f"Task {task_id}: ValidationError on attempt {attempt}. Retrying...")
            if attempt == MAX_RETRIES:
                logger.info(
                    f"Task {task_id}: Validation failed after {MAX_RETRIES} attempts. Skipping."
                )
                return None

        except Exception as e:
            logger.info(f"Task {task_id}: Unexpected error processing document {codigo}: {e}")
            if attempt == MAX_RETRIES:
                return None

    return None


def process_documents(client):
    sample = utils.read_json_to_dict_of_samples()
    logger.info(f"Total documents to process: {len(sample)}")
    results = {}

    for task_id, codigo in enumerate(sample, start=1):
        result = extract(
            client,
            task_id,
            codigo,
            utils.clean_html_text(
                "Nome do Documento: "
                + sample[codigo].titulo
                + "\nCorpo:"
                + sample[codigo].texto
            ),
            PROMPT,
        )
        results[codigo] = result

    logger.info("All extractions completed.")
    return results


def run():
    logger.info("Starting experiments")

    client_db = get_connection()
    init_db(client_db)
    description = "Sixth Attempt"
    experiment = repository.get_experiment(client_db, description)

    if not experiment:
        logger.info("Experiment not found. Starting new experiment.")

        client = ollama.Client(host=OLLAMA_HOST)
        extraction_results = process_documents(client)

        metric = evaluate_extraction_per_column(
            extraction_results, utils.read_csv_to_dict_of_ground_truth()
        )

        data = utils.serialize_experiment(description, MODEL_NAME, OPTIONS, metric, PROMPT, models.Licitação.model_json_schema(), extraction_results, utils.read_csv_to_dict_of_ground_truth())
        repository.save_experiment(
            client_db,
            data["description"],
            data["model"],
            str(data["options"]),
            str(data["metrics"]),
            data["prompt"],
            str(data["schema"]),
            str(data["serializable"]),
            str(data["ground_truth"]),
        )
    else:
        evaluate_extraction_per_column(
            utils.load_experiment(experiment), utils.read_csv_to_dict_of_ground_truth()
        )
