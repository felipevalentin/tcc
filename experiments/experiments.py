import asyncio
import ollama
import utils
import models
import time
from pydantic import ValidationError  # Import ValidationError for handling retries

OLLAMA_HOST = "https://ollama-dev.ceos.ufsc.br/"
MODEL_NAME = "qwen2.5:0.5b"
MAX_RETRIES = 3          # Number of retry attempts for validation errors
CONCURRENT_REQUESTS = 10 # Control the number of concurrent requests
NUM_CLIENTS = 2          # Use at least 2 clients to test the speed

async def extract(client, semaphore, task_id, codigo, context):
    """Extract data from a document asynchronously, retrying on ValidationError."""
    async with semaphore:
        for attempt in range(1, MAX_RETRIES + 1):
            print(f"Task {task_id}: Starting extraction for document {codigo} (Attempt {attempt})")
            try:
                response = await client.chat(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "Extraia os atributos do documento"},
                        {"role": "user", "content": context},
                    ],
                    format=models.GroundTruthExtractedFields.model_json_schema(),
                )
                content = response["message"]["content"]
                extracted_data = models.GroundTruthExtractedFields.model_validate_json(content)

                print(f"Task {task_id}: Finished extraction for document {codigo}")
                return extracted_data

            except ValidationError as e:
                print(f"Task {task_id}: ValidationError on attempt {attempt}. Retrying...")
                if attempt == MAX_RETRIES:
                    print(f"Task {task_id}: Validation failed after {MAX_RETRIES} attempts. Skipping.")
                    return None

            except Exception as e:
                print(f"Task {task_id}: Unexpected error processing document {codigo}: {e}")
                return None  # Do not retry on general errors

async def process_documents(clients, semaphore):
    """Process all documents asynchronously with limited concurrency using multiple clients."""
    sample = utils.read_json_to_dict_of_samples()
    print(f"Total documents to process: {len(sample)}")

    # Distribute tasks among the available clients using round-robin scheduling
    tasks = [
        extract(clients[task_id % len(clients)], semaphore, task_id, codigo, sample[codigo].texto)
        for task_id, codigo in enumerate(sample, start=1)
    ]

    results = await asyncio.gather(*tasks)
    print("All extractions completed.")

    # Print each GroundTruthExtractedFields object (if extraction was successful)
    for result in results:
        if result is not None:
            print(result)

    return results

async def main():
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    # Create a list of clients according to NUM_CLIENTS
    clients = [ollama.AsyncClient(host=OLLAMA_HOST) for _ in range(NUM_CLIENTS)]

    print("Starting document processing...")
    results = await process_documents(clients, semaphore)
    print("Processing completed.")

if __name__ == "__main__":
    start_time = time.perf_counter()  # Start timing
    asyncio.run(main())
    end_time = time.perf_counter()  # End timing

    print(f"Total execution time: {end_time - start_time:.2f} seconds")