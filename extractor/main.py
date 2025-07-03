import html
import json
import time
from typing import Dict, List

import config
import log
import models
import ollama
import prompt
import utils

logger = log.get_logger(__name__)


def extract(client, prompts, key, task_id):
    logger.info(f"Task {task_id}: Starting extraction for document {key}")
    start_time = time.perf_counter()

    stream = client.chat(
        model=config.MODEL,
        messages=prompts,
        format=models.Licitacao.model_json_schema(),
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

    extracted_data = models.Licitacao.model_validate_json(full_content, strict=True)

    logger.info(
        "Task %s: Finished extraction for document %s in %.2f s",
        task_id,
        key,
        time.perf_counter() - start_time,
    )
    return extracted_data.model_dump()


def create_prompt(title: str, body: str) -> List[Dict[str, str]]:
    body = utils.clean_html_text(body)
    contexto = f"""# Contexto
## Nome do Documento
{title}

## Texto do Documento
{body}
"""
    prompts = [
        {"role": "system", "content": prompt.PROMPT.replace("{CONTEXTO}", contexto)},
    ]
    return prompts


def process_publications():
    client = ollama.Client(host=config.OLLAMA_HOST)
    for file in config.INPUT_PATH.iterdir():
        publications = json.loads(file.read_text(encoding="utf-8"))
        raw_publications = {
            item["codigo"]: models.RawPublication(
                **{**item, "texto": html.unescape(item["texto"])}
            )
            for item in publications
        }
        results = {}

        for task_id, key in enumerate(raw_publications):
            prompts = create_prompt(
                raw_publications[key].titulo, raw_publications[key].texto
            )
            result = extract(client, prompts, key, task_id)

            if result is not None:
                results[key] = result
        output_path = config.OUTPUT_PATH / f"{file.stem}.json"
        output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))


def main():
    process_publications()


if __name__ == "__main__":
    main()
