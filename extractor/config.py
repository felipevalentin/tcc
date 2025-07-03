import pathlib

OLLAMA_HOST = "https://ollama-dev.ceos.ufsc.br/"
MODEL = "llama3.3:70b"
OPTIONS = {
    "temperature": 0,
    "seed": 42,
}
INPUT_PATH = pathlib.Path("./resources/input")
OUTPUT_PATH = pathlib.Path("./resources/output")
