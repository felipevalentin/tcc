import config
import models
import log
import time

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


