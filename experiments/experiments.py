import json
import pathlib
import time
import ollama
import utils
import models
import hashlib
from pydantic import ValidationError

OLLAMA_HOST = "https://ollama-dev.ceos.ufsc.br/"
PROMPT = "Extraia os atributos do documento"
MODEL_NAME = "llama3.3:70b"
MAX_RETRIES = 3

def extract(client, task_id, codigo, context):
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"Task {task_id}: Starting extraction for document {codigo} (Attempt {attempt})")
        try:
            start_time = time.perf_counter()
            response = client.chat(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": context},
                ],
                format=models.GroundTruthExtractedFields.model_json_schema(),
            )
            content = response["message"]["content"]
            extracted_data = models.GroundTruthExtractedFields.model_validate_json(content)
            print(f"Task {task_id}: Finished extraction for document {codigo} in {time.perf_counter() - start_time:.2f} seconds")
            return extracted_data
        except ValidationError as e:
            print(f"Task {task_id}: ValidationError on attempt {attempt}. Retrying...")
            if attempt == MAX_RETRIES:
                print(f"Task {task_id}: Validation failed after {MAX_RETRIES} attempts. Skipping.")
                return None

        except Exception as e:
            print(f"Task {task_id}: Unexpected error processing document {codigo}: {e}")
            return None

def process_documents(client):
    sample = utils.read_json_to_dict_of_samples()
    print(f"Total documents to process: {len(sample)}")
    results = {}

    for task_id, codigo in enumerate(sample, start=1):
        result = extract(client, task_id, codigo, sample[codigo].texto)
        results[codigo] = result

    print("All extractions completed.")
    return results


def evaluate_extraction_per_column(extraction_results, ground_truth):
    corrects = {field: 0 for field in models.GroundTruthExtractedFields.model_fields.keys()}
    for codigo in ground_truth:
        extraction_dump = extraction_results[codigo].model_dump()
        ground_truth_dump = ground_truth[codigo].model_dump()
        print(f"\nEvaluating document {codigo}...")
        for field in models.GroundTruthExtractedFields.model_fields.keys():
            if extraction_dump[field] == ground_truth_dump[field]:
                corrects[field] += 1
                print(f"Field '{field}' is correct.")
            else:
                print(f"Field '{field}' is incorrect - Expected: {ground_truth_dump[field]}, Got: {extraction_dump[field]}")

    total = len(ground_truth)
    metrics = {}
    for field in models.GroundTruthExtractedFields.model_fields.keys():
        metrics[field] = {
            "accuracy": corrects[field] / total,
        }
    # pretty print metrics in a single line
    print("\nEvaluation Metrics (Accuracy):")
    for field, metric in metrics.items():
        print(f"{field}: {metric['accuracy']:.2%}", end=", ")

def main():
    print("Starting document processing...")
    prompt_hash = hashlib.md5(f"{PROMPT} + {MODEL_NAME}".encode()).hexdigest()
    if not pathlib.Path(f"../resources/{prompt_hash}.json").exists():
        print("Prompt hash file not found. Processing documents...")
        client = ollama.Client(host=OLLAMA_HOST)
        extraction_results = process_documents(client)
        print("Processing completed.")
        serializable_results = {
            codigo: result.model_dump()
            for codigo, result in extraction_results.items()
            if result is not None
        }
        with open(f"../resources/{prompt_hash}.json", "w+") as f:
            json.dump(serializable_results, f, indent=4, default=str)
    else:
        print("Prompt hash file found. Loading existing results...")
        with open(f"../resources/{prompt_hash}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            extraction_results = {codigo: models.GroundTruthExtractedFields(**fields) for codigo, fields in data.items()}

    evaluate_extraction_per_column(extraction_results, utils.read_csv_to_dict_of_ground_truth())

if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")
