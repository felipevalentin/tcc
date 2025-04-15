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
PROMPT = """Você é um assistente especializado na extração de informações de licitações. 
Extraia as seguintes informações de um documento de licitação:

- Raciocínio: empregado na extração dos campos abaixo.
- Nome Do Documento: Presente no título do documento.
- Número Do Processo Administrativo
- Município: de Santa Catarina onde ocorreu a licitação.
- Modalidade: da licitação.
- Formato Da Modalidade (opcional): Presencial ou Eletrônica.
- Número Da Modalidade: da licitação.
- Objeto: Descrição completa do objeto da licitação, material ou serviço.
- Data De Abertura (opcional): Data de abertura do processo licitatório.
- Informações Do Edital (opcional): onde o edital pode ser encontrado.
- Signatário (opcional): Nome da pessoa que assinou o documento.
- Cargo Do Signatário (opcional): Cargo da pessoa que assinou o documento. 

Retorne como JSON.
"""
# Signatário pode ser um campo complexo com nome e cargo e podemos ter uma lista de signatários
# Modalidade pode ser um campo complexo, com Modalidade, Formato e Número
# Informações pode ter um nome melhor -> Informações do Edital, com endereço físico, telefone e lista de sites.
# Data de Abertura pode ser um campo complexo
MODEL_NAME = "llama3.3:70b"
MAX_RETRIES = 3


def extract(client, task_id, codigo, context, prompt):
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
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": context},
                ],
                format=models.Licitação.model_json_schema(),
                options={
                    "temperature": 0,
                    "seed": 42,
                },
            )
            content = response["message"]["content"]
            extracted_data = models.Licitação.model_validate_json(
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
                prompt += f"\n {msg}\n"
            if attempt == MAX_RETRIES:
                print(
                    f"Task {task_id}: Validation failed after {MAX_RETRIES} attempts. Skipping."
                )
                return None

        except Exception as e:
            print(f"Task {task_id}: Unexpected error processing document {codigo}: {e}")
            prompt += f"\n answer faster in less than 1 minute\n"
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
            clean_html_text("Título: " + sample[codigo].titulo + "\n\n" + sample[codigo].texto),
            PROMPT,
        )
        results[codigo] = result
        return results

    print("All extractions completed.")
    return results


def evaluate_extraction_per_column(extraction_results, ground_truth):
    corrects = {
        field: 0 for field in models.Licitação.model_fields.keys()
    }
    null = {field: 0 for field in models.Licitação.model_fields.keys()}
    # compare with data_abertura normalizada
    for codigo in ground_truth:
        try:
            extraction_dump = extraction_results[codigo].model_dump()
            ground_truth_dump = ground_truth[codigo].model_dump()
        except Exception as e:
            print(f"Task {codigo}: KeyError: {e}")
            break
        print(f"\nEvaluating document {codigo}...")
        for field in models.Licitação.model_fields.keys():
            if field == "raciocínio":
                continue
            nomralized_extracted = extraction_dump[field]
            normalized_ground_truth = ground_truth_dump[field]
            if normalized_ground_truth is None:
                null[field] += 1
            if nomralized_extracted is None and normalized_ground_truth is None:
                corrects[field] += 1
                # print(f"Field '{field}' is correct.")
                continue

            if (
                field != "data_de_abertura"
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

            if field == "data_de_abertura":
                normalized_ground_truth = ground_truth_dump[field + "_normalizada"]
                if (
                    nomralized_extracted
                    and normalized_ground_truth
                    and nomralized_extracted.strftime("%Y-%m-%dT%H:%M")
                    == normalized_ground_truth.strftime("%Y-%m-%dT%H:%M")
                ):
                    corrects[field] += 1
                else:
                    print(
                        f"Field '{field}' is incorrect - Expected: {ground_truth_dump[field + "_normalizada"]}, Got: {extraction_dump[field]}"
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
                if field == "tipo_documento":
                    print(f"titulo: {ground_truth_dump["titulo"]}")
                print(
                    f"Field '{field}' is incorrect - Expected: {ground_truth_dump[field]}, Got: {extraction_dump[field]}"
                )

    total = len(ground_truth)
    metrics = {}
    for field in models.Licitação.model_fields.keys():
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
    return metrics


def main():
    print("Starting document processing...")
    prompt_hash = hashlib.md5(
        f"{PROMPT} + {MODEL_NAME} + {models.Licitação.model_json_schema()}".encode()
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
        metrics =         evaluate_extraction_per_column(
            extraction_results, utils.read_csv_to_dict_of_ground_truth()
        )
        save_doc = {
            "time": datetime.datetime.now().isoformat(),
            "metrics": metrics,
            "prompt": PROMPT,
            "model": MODEL_NAME,
            "schema": models.Licitação.model_json_schema(),
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
                codigo: models.Licitação.model_validate(fields)
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
