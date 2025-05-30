import hashlib
import os
from typing import List, Tuple, Dict

import chromadb
from transformers import AutoModel, AutoTokenizer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


CHROMA_PATH = "./chroma/rag"
COLLECTION_NAME = "chunks"
MODEL_ID = "neuralmind/bert-large-portuguese-cased"

QUERIES = [
    "Tipo do documento",
    "Número do processo administrativo",
    "Município",
    "Modalidade",
    "Formato da modalidade",
    "Número da modalidade",
    "Objeto",
    "Data de abertura",
    "Site do edital",
    "Nome do Signatário",
    "Cargo do signatário",
]


def _get_model_tokenizer_embedding():
    model = AutoModel.from_pretrained(MODEL_ID)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, do_lower_case=False)
    embedding = HuggingFaceEmbeddings(
        model_name=MODEL_ID,
        model_kwargs={"device": "mps"},
        encode_kwargs={"normalize_embeddings": False},
    )
    return model, tokenizer, embedding

_MODEL, _TOKENIZER, _EMBEDDING = _get_model_tokenizer_embedding()

def _chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    len_token = lambda x: len(_TOKENIZER.tokenize(x))
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len_token,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_text(text)
    return chunks


os.makedirs(CHROMA_PATH, exist_ok=True)
client = chromadb.Client()


def _doc_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _chunk_id(doc_id: str, chunk_size: int, overlap: int, idx: int) -> str:
    return f"{doc_id}_{chunk_size}_{overlap}_{idx}"


def get_chunks(
    text: str,
    chunk_size: int = 256,
    overlap: int = 64,
    top_k: int = 5,
) -> Tuple[str, Dict]:
    try:
        client.delete_collection(COLLECTION_NAME)
    except:
        print("no collection")
    client.create_collection(
        COLLECTION_NAME
    )
    vector_store_from_client = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=_EMBEDDING,
    )
    doc_id = _doc_id(text)

    print("chunking")
    chunks = _chunk_text(text, chunk_size, overlap)

    ids, documents = [], []
    for idx, chunk in enumerate(chunks):
        cid = _chunk_id(doc_id, chunk_size, overlap, idx)
        ids.append(cid)
        documents.append(Document(chunk, id=cid, metadata={"doc_id": doc_id}))

    vector_store_from_client.add_documents(
        ids=ids,
        documents=documents,
    )

    print("querying")
    results = {}
    for query in QUERIES:
        result: List[Document] = vector_store_from_client.similarity_search(
            query=query,
            k=min(top_k, len(chunks)),
            filter={"doc_id": doc_id},
        )
        results[query] = [r.page_content for r in result]

    return doc_id, results
