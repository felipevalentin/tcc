import ollama
import models
import utils
import json

client = ollama.Client(host="https://ollama-dev.ceos.ufsc.br/")
response = client.list()
for model in response.models:
    print(model.model, model.details.parameter_size)


def extract(context):
    return client.chat(
        model="qwen2.5:0.5b",
        messages=[
            {"role": "system", "content": "Extraia os atributos do documento"},
            {"role": "user", "content": context},
        ],
        format=models.Atributos.model_json_schema(),
    )


sample = utils.get_sample()
ground_truth = utils.get_ground_truth()
for codigo in sample:
    response = extract(sample[codigo]["texto"])
    content = response["message"]["content"]
    content_json = json.loads(content)
    print(models.Atributos.model_validate_json(content))
    print(content_json)
