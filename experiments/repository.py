import hashlib
from datetime import UTC, datetime
from sqlite3 import Connection, connect

from logger import get_logger

logger = get_logger(__name__)

def generate_hash_key(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def get_connection(path: str = "experiments.db"):
    logger.info(f"Connecting to database at {path}")
    connection = connect(path)
    logger.info("Connected to database")
    return connection


def init_db(conn: Connection) -> None:
    logger.info("Initializing database")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
        id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL,
        description TEXT NOT NULL,
        model TEXT NOT NULL,
        options TEXT NOT NULL,
        metrics TEXT NOT NULL,
        prompt TEXT NOT NULL,
        schema TEXT NOT NULL,
        output TEXT NOT NULL,
        ground_truth TEXT NOT NULL);
    """)
    conn.commit()
    logger.info("Database initialized")


def save_experiment(
    conn: Connection,
    description: str,
    model: str,
    options: str,
    metrics: str,
    prompt: str,
    schema: str,
    output: str,
    ground_truth: str,
) -> None:
    logger.info("Saving experiment")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO experiments (id, created_at, description, model, options, metrics, prompt, schema, output, ground_truth)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            generate_hash_key(description),
            datetime.now(UTC).isoformat(),
            description,
            model,
            options,
            metrics,
            prompt,
            schema,
            output,
            ground_truth,
        ),
    )
    conn.commit()
    logger.info("Experiment saved")
