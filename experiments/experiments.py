import html
import pathlib
import re
import time
import sqlite3
import datetime
import json
import examples

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
Sua tarefa é ler um texto de licitação e extrair as seguintes informações **exatamente como aparecem no texto**, retornando um JSON estruturado conforme o modelo abaixo:

- Tipo Do Documento (Opcional): Qual o tipo do documento, Exemplo Aviso de Licitação Se não informado retorne null.
- Número Do Processo Administrativo: deve seguir o formato número/ano, como por exemplo "12/2024, quando ausente igual ao número da modalidade".
- Município: de Santa Catarina onde ocorreu a licitação.
- Modalidade: da licitação.
- Formato Da Modalidade (opcional): Presencial ou Eletrônica. Se não informado retorne null.
- Número Da Modalidade: da licitação. Deve seguir o formato número/ano, como por exemplo "12/2024".
- Objeto: Extraia **exatamente como descrito no documento** o objeto da licitação, sem resumir, adicionar texto, reescrever ou interpretar.
- Data De Abertura (opcional): extraia a **data e horário completos** da abertura do processo licitatório no formato ISO 8601 (exemplo: `2024-10-13T10:30`). **NÃO invente uma data.** Se não informado retorne null.
    * não extrair se não estiver informado que é de abertura ou início de sessão.
- Site Do Edital (opcional): apenas se o endereço do site estiver no texto, não inferir a partir de email. exemplo www.saolourenco.sc.gov.br. Se não informado retorne null.
    * não extrair se não estiver informado que é onde pode ser encontrado o edital.
- Signatário (opcional): Nome da pessoa que assinou o documento. Se não informado retorne null.
- Cargo Do Signatário (opcional): Cargo da pessoa que assinou o documento. Se não informado retorne null.

**Responda em Json**
Se não informado retorne null.

**Exemplo 1 de entrada**
{EXEMPLO_1}

**Exemplo 1 de saída**
{EXEMPLO_1_OUTPUT}
"""
# objeto ajustar
# nome do documento ajustar
# Signatário pode ser um campo complexo com nome e cargo e podemos ter uma lista de signatários
# Modalidade pode ser um campo complexo, com Modalidade, Formato e Número
# Informações pode ter um nome melhor -> Informações do Edital, com endereço físico, telefone e lista de sites.
# Data de Abertura pode ser um campo complexo ou string com validação
MODEL_NAME = "llama3.3:70b"
OPTIONS = {
    "temperature": 0,
    "seed": 42,
}
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
                    {
                        "role": "system",
                        "content": prompt
                        # .replace(
                        #     "{SCHEMA}", str(models.Licitação.model_json_schema())
                        # )
                        .replace("{EXEMPLO_1}", examples.EXAMPLE_1).replace(
                            "{EXEMPLO_1_OUTPUT}", examples.EXAMPLE_1_OUTPUT
                        ),
                        # .replace(
                        #     "{EXEMPLO_2}", examples.EXAMPLE_2
                        # )
                        # .replace(
                        #     "{EXEMPLO_2_OUTPUT}", examples.EXAMPLE_2_OUTPUT
                        # )
                        # .replace(
                        #     "{EXEMPLO_3}", examples.EXAMPLE_3
                        # )
                        # .replace(
                        #     "{EXEMPLO_3_OUTPUT}", examples.EXAMPLE_3_OUTPUT
                        # ),
                    },
                    {"role": "user", "content": f"**CONTEXTO**\n{context}"},
                ],
                format=models.Licitação.model_json_schema(),
                options=OPTIONS,
            )
            content = response["message"]["content"]
            extracted_data = models.Licitação.model_validate_json(content, strict=True)
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
            return None

        except Exception as e:
            print(f"Task {task_id}: Unexpected error processing document {codigo}: {e}")
            prompt += f"\n answer faster in less than 1 minute\n"
            if attempt == MAX_RETRIES:
                return None
            return None
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
            clean_html_text(
                "Nome do Documento: "
                + sample[codigo].titulo
                + "\nCorpo:"
                + sample[codigo].texto
            ),
            PROMPT,
        )
        results[codigo] = result

    print("All extractions completed.")
    return results


def evaluate_extraction_per_column(extraction_results, ground_truth):
    corrects = {field: 0 for field in models.Licitação.model_fields.keys()}
    corrects_actual_positives = {
        field: 0 for field in models.Licitação.model_fields.keys()
    }
    everything_classified_as_positive = {
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

            if nomralized_extracted is not None:
                everything_classified_as_positive[field] += 1

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

            if field in ["numero_do_processo_licitatório", "número_da_modalidade"]:
                nomralized_extracted = nomralized_extracted.strip().lstrip("0")
                normalized_ground_truth = normalized_ground_truth.strip().lstrip("0")

            if field == "data_de_abertura":
                if (
                    nomralized_extracted
                    and normalized_ground_truth
                    and nomralized_extracted
                    == normalized_ground_truth.strftime("%Y-%m-%dT%H:%M")
                ):
                    corrects[field] += 1
                    corrects_actual_positives[field] += 1
                else:
                    print(
                        f"Field '{field}' is incorrect - Expected: {ground_truth_dump[field]}, Got: {extraction_dump[field]}"
                    )
            elif field in [
                "objeto",
            ]:
                distance = Levenshtein.ratio(
                    nomralized_extracted, normalized_ground_truth
                )
                print(f"Levenshtein distance for field '{field}': {distance}")
                if distance > 0.9:
                    corrects[field] += 1
                    corrects_actual_positives[field] += 1
                # print(f"Field '{field}' is correct.")
                else:
                    print(
                        f"Field '{field}' is incorrect - \nExpected: <{ground_truth_dump[field]}> \nGot: <{extraction_dump[field]}>"
                    )
            elif nomralized_extracted == normalized_ground_truth:
                corrects[field] += 1
                corrects_actual_positives[field] += 1
            # print(f"Field '{field}' is correct.")
            else:
                if field == "tipo_documento":
                    print(f"titulo: {ground_truth_dump['titulo']}")
                print(
                    f"Field '{field}' is incorrect - Expected: {ground_truth_dump[field]}, Got: {extraction_dump[field]}"
                )

    total_classifications = len(ground_truth)
    all_actual_positives = dict()
    for field in models.Licitação.model_fields.keys():
        if field == "raciocínio":
            continue
        all_actual_positives[field] = 0
        for codigo in ground_truth:
            all_actual_positives[field] += (
                ground_truth[codigo].model_dump()[field] is not None
            )

    metrics = {}
    for field in models.Licitação.model_fields.keys():
        if field == "raciocínio":
            continue
        metrics[field] = {
            "accuracy": corrects[field] / total_classifications,
            "recall": corrects_actual_positives[field] / all_actual_positives[field],
        }
        if everything_classified_as_positive[field] > 0:
            metrics[field]["precision"] = (
                corrects_actual_positives[field]
                / everything_classified_as_positive[field]
            )
        else:
            metrics[field]["precision"] = 0

        if metrics[field]["precision"] + metrics[field]["recall"] == 0:
            metrics[field]["f1-score"] = 0
        else:
            metrics[field]["f1-score"] = (
                2
                * (metrics[field]["precision"] * metrics[field]["recall"])
                / (metrics[field]["precision"] + metrics[field]["recall"])
            )

    # pretty print metrics in a single line
    print("\nEvaluation Metrics (Accuracy):")
    print("\n\nCore metrics:")
    for field, metric in metrics.items():
        if field == "raciocínio":
            continue
        print(f"{field}:")
        for k, v in metric.items():
            print(f"  {k}: {v:.2%}", end=", ")
        print()

    print()
    for field in null:
        if field == "raciocínio":
            continue
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
        metrics = evaluate_extraction_per_column(
            extraction_results, utils.read_csv_to_dict_of_ground_truth()
        )
        save_doc = {
            "metrics": metrics,
            "prompt": PROMPT,
            "options": OPTIONS,
            "model": MODEL_NAME,
            "schema": models.Licitação.model_json_schema(),
            "serializable": serializable_results,
        }
        with open(f"../resources/{prompt_hash}.json", "w+") as f:
            # save prompt and model schema
            json.dump(save_doc, f, indent=4, ensure_ascii=False)
    else:
        print(f"Prompt hash file found. {prompt_hash} Loading existing results...")
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
    text_limited_breaks = re.sub(r"\n+", "\n", text_utf8)

    return text_limited_breaks.strip()


def init_db(path="experiments.db"):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    # noinspection SqlNoDataSourceInspection
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            description TEXT NOT NULL,
            model TEXT NOT NULL,
            options TEXT NOT NULL,
            metrics TEXT NOT NULL,
            prompt TEXT NOT NULL,
            schema TEXT NOT NULL,
            output TEXT NOT NULL,
        )
    """)
    conn.commit()
    return conn


def save_experiment(conn, description, model, options, metrics, prompt, schema, output):
    cursor = conn.cursor()
    # noinspection SqlNoDataSourceInspection
    cursor.execute(
        """
        INSERT INTO experiments (created_at, description, model, options, metrics, prompt, schema, output)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            datetime.datetime.now(datetime.UTC).isoformat(),
            description,
            prompt,
            json.dumps(schema, ensure_ascii=False),
            json.dumps(metrics, ensure_ascii=False),
            json.dumps(output, ensure_ascii=False),
        ),
    )
    conn.commit()


if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")
