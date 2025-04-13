import datetime
import html
import json
import pathlib
import re
import time

import Levenshtein
import ollama
import unidecode
from bs4 import BeautifulSoup

import utils
import models
import hashlib
from pydantic import ValidationError

OLLAMA_HOST = "https://ollama-dev.ceos.ufsc.br/"
PROMPT = """Você é um assistente especializado na extração de informações de licitações de aquisição realizadas no Brasil. Sua tarefa é ler cuidadosamente um texto de licitação e identificar as informações necessárias para preenchimento dos campos descritos. A saída deve ser um JSON válido, seguindo rigorosamente o esquema especificado, sem incluir informações ou comentários adicionais."""
MODEL_NAME = "llama3.3:70b"
MAX_RETRIES = 3


def extract(client, task_id, codigo, context):
    global PROMPT
    for attempt in range(1, MAX_RETRIES + 1):
        print(
            f"Task {task_id}: Starting extraction for document {codigo} (Attempt {attempt})"
        )
        try:
            start_time = time.perf_counter()
            response = client.chat(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": context},
                ],
                format=models.GroundTruthExtractedFields.model_json_schema(),
                options={
                    "temperature": 0,
                },
            )
            content = response["message"]["content"]
            extracted_data = models.GroundTruthExtractedFields.model_validate_json(
                content, strict=True
            )
            print(
                f"Task {task_id}: Finished extraction for document {codigo} in {time.perf_counter() - start_time:.2f} seconds"
            )
            return extracted_data
        except ValidationError as e:
            print(f"Task {task_id}: ValidationError on attempt {attempt}. Retrying...")
            for error in e.errors():
                msg = error["ctx"]["error"]
                PROMPT += f"\n {msg}\n"
            if attempt == MAX_RETRIES:
                print(
                    f"Task {task_id}: Validation failed after {MAX_RETRIES} attempts. Skipping."
                )
                return None

        except Exception as e:
            print(f"Task {task_id}: Unexpected error processing document {codigo}: {e}")
            if attempt == MAX_RETRIES:
                return None


def process_documents(client):
    sample = utils.read_json_to_dict_of_samples()
    print(f"Total documents to process: {len(sample)}")
    results = {}

    for task_id, codigo in enumerate(sample, start=1):
        result = extract(
            client,
            task_id,
            codigo,
            clean_html_text(sample[codigo].titulo + "\n" + sample[codigo].texto),
        )
        results[codigo] = result

    print("All extractions completed.")
    return results


def evaluate_extraction_per_column(extraction_results, ground_truth):
    corrects = {
        field: 0 for field in models.GroundTruthExtractedFields.model_fields.keys()
    }
    null = {field: 0 for field in models.GroundTruthExtractedFields.model_fields.keys()}
    # compare with data_abertura normalizada
    for codigo in ground_truth:
        try:
            extraction_dump = extraction_results[codigo].model_dump()
            ground_truth_dump = ground_truth[codigo].model_dump()
        except KeyError as e:
            print(f"Task {codigo}: KeyError: {e}")
            return
        print(f"\nEvaluating document {codigo}...")
        for field in models.GroundTruthExtractedFields.model_fields.keys():
            nomralized_extracted = extraction_dump[field]
            normalized_ground_truth = ground_truth_dump[field]
            if nomralized_extracted is None and normalized_ground_truth is None:
                null[field] += 1
                corrects[field] += 1
                # print(f"Field '{field}' is correct.")
                continue

            if (
                field != "data_abertura"
                and extraction_dump[field]
                and ground_truth_dump[field]
            ):
                nomralized_extracted = (
                    unidecode.unidecode(extraction_dump[field]).replace(" ", "").lower()
                )
                normalized_ground_truth = (
                    unidecode.unidecode(ground_truth_dump[field])
                    .replace(" ", "")
                    .lower()
                )

            if field == "data_abertura":
                normalized_ground_truth = ground_truth_dump[field + "_normalizada"]
                if (
                    nomralized_extracted
                    and normalized_ground_truth
                    and nomralized_extracted.strftime("%Y-%m-%dT%H:%M")
                    == normalized_ground_truth.strftime("%Y-%m-%dT%H:%M")
                ):
                    corrects[field] += 1
                    print(
                        f"correct extracted: {nomralized_extracted} ground truth: {normalized_ground_truth}"
                    )
                else:
                    print(
                        f"wrong extracted: {nomralized_extracted} / {normalized_ground_truth}"
                    )
            elif field in [
                "objeto",
                "justificativa",
                "informacoes",
                "signatario",
                "cargo_do_signatario",
            ]:
                distance = Levenshtein.ratio(
                    nomralized_extracted, normalized_ground_truth
                )
                print(f"Levenshtein distance for field '{field}': {distance}")
                if distance > 0.9:
                    corrects[field] += 1
                    # print(f"Field '{field}' is correct.")
                else:
                    print(
                        f"Field '{field}' is incorrect - Expected: <{ground_truth_dump[field]}> Got: <{extraction_dump[field]}>"
                    )
            elif nomralized_extracted == normalized_ground_truth:
                corrects[field] += 1
                # print(f"Field '{field}' is correct.")
            else:
                print(
                    f"Field '{field}' is incorrect - Expected: {ground_truth_dump[field]}, Got: {extraction_dump[field]}"
                )

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

    print()
    for field in null:
        print(f"{field}: {null[field]}", end=", ")


def main():
    print("Starting document processing...")
    prompt_hash = hashlib.md5(
        f"{PROMPT} + {MODEL_NAME} + {models.GroundTruthExtractedFields.model_json_schema()}".encode()
    ).hexdigest()
    if not pathlib.Path(f"../resources/{prompt_hash}.json").exists():
        print("Prompt hash file not found. Processing documents...")
        client = ollama.Client(host=OLLAMA_HOST)
        extraction_results = process_documents(client)
        print("Processing completed.")
        serializable_results = {
            codigo: result.model_dump(mode="json")
            for codigo, result in extraction_results.items()
            if result is not None
        }
        save_doc = {
            "time": datetime.datetime.now().isoformat(),
            "prompt": PROMPT,
            "model": MODEL_NAME,
            "schema": models.GroundTruthExtractedFields.model_json_schema(),
            "serializable": serializable_results,
        }
        with open(f"../resources/{prompt_hash}.json", "w+") as f:
            # save prompt and model schema
            json.dump(save_doc, f, indent=4, ensure_ascii=False)
    else:
        print("Prompt hash file found. Loading existing results...")
        with open(f"../resources/{prompt_hash}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            serializable_results = data["serializable"]
            extraction_results = {
                codigo: models.GroundTruthExtractedFields.model_validate(fields)
                for codigo, fields in serializable_results.items()
            }
    evaluate_extraction_per_column(
        extraction_results, utils.read_csv_to_dict_of_ground_truth()
    )


def clean_html_text(input_text):
    soup = BeautifulSoup(input_text, "html.parser")
    text_without_html = soup.get_text()
    text_utf8 = html.unescape(text_without_html)
    text_limited_breaks = re.sub(r"\n{3,}", "\n\n", text_utf8)

    return text_limited_breaks.strip()


if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")
