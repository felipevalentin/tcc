import pathlib

OLLAMA_HOST = "https://ollama-dev.ceos.ufsc.br/"
OPTIONS = {
    "temperature": 0,
    "seed": 42,
}
PROMPTS_PATH = pathlib.Path("./resources/prompts")
RESULTS_PATH = pathlib.Path("./resources/results")
