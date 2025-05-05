from time import perf_counter

from experiments import run
from logger import get_logger

logger = get_logger(__name__)


def main():
    start_time = perf_counter()
    run()
    end_time = perf_counter()
    logger.info(f"Total execution time: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
