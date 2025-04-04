import asyncio
import ollama
import models
import utils
import json


async def extract(client, context):
    PROMPT = {
        "model": "qwen2.5:0.5b",
        "messages": [
            {"role": "system", "content": "Extraia os atributos do documento"},
            {"role": "user", "content": context},
        ],
        "format": models.Atributos.model_json_schema(),
    }

    return client.chat(**PROMPT)


async def process_documents():
    """Process multiple documents asynchronously."""
    sample = utils.read_json_to_dict_of_samples()

    async with ollama.AsyncClient(host="https://ollama-dev.ceos.ufsc.br/") as client:
        tasks = [extract(client, sample[codigo]["texto"]) for codigo in sample]
        results = await asyncio.gather(*tasks)

    for result in results:
        if result:
            print(result)
