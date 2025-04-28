import chromadb
import torch
from transformers import AutoModel, AutoTokenizer

OLLAMA_HOST = "https://ollama-dev.ceos.ufsc.br/"

EXAMPLE_1 = """Titulo: HOMOLOGAÇÃO DE PREGÃO ELETRÔNICO 34/2022
Corpo: REPUBLICAÇÃO EDITAL DE PREGÃO ELETRÔNICO Nº 34/2022
O FUNDO MUNICIPAL DE SAÚDE DE CURITIBANOS, Estado de Santa Catarina, torna público, para quem interessar possa, que fará realizar licitação na modalidade pregão, sob a forma Eletrônico, através do site www.portaldecompraspublicas.com.br, do tipo Menor Preço Global o qual será processado e julgado em conformidade com a Lei Federal nº. 10.520/02, Decreto Federal 10.024/19, Lei Complementar nº 123/06, Decreto Municipal 5338/2020 com aplicação subsidiária da Lei Federal nº. 8.666/93, e suas respectivas alterações e legislação aplicável, pelo Pregoeiro e sua Equipe de Apoio, designados pela Portaria n° 426/2020, cujo objeto é a AQUISIÇÃO DE SISTEMA DE INFORMÁTICA PARA REGISTRO, TRATAMENTO E TRANSMISSÃO DE DADOS DOS SERVIÇOS E ATENDIMENTOS DE SAÚDE NO ÂMBITO DO MUNICÍPIO DE CURITIBANOS, CONFORME TERMO DE REFERÊNCIA. Sendo que a proposta deve ser apresentada até o dia e hora abaixo especificados.
DATA DE APRESENTAÇÃO DA PROPOSTA: ATÉ DIA 23/06/2022
HORÁRIO LIMITE: até 13h15 min.
DATA DE ABERTURA DA SESSÃO: DIA 23/06/2022 HORÁRIO: às 13h16min.
Curitibanos, 06 de junho de 2022.
Local da retirada do Edital e Anexos: 
www.curitibanos.sc.gov.br e Portal de Compras Públicas 
Roque Stanguerlin
Presidente do Fundo"""

documents = [EXAMPLE_1]

# chunking
chunks = []
chunk_size = 300  # number of characters per chunk
overlap = 50  # number of characters that overlap between chunks

for document in documents:
    start = 0
    while start < len(document):
        end = start + chunk_size
        chunk = document[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

# Load model without pretraining heads (only embeddings)
model = AutoModel.from_pretrained("neuralmind/bert-large-portuguese-cased")
tokenizer = AutoTokenizer.from_pretrained(
    "neuralmind/bert-large-portuguese-cased", do_lower_case=False
)

client = chromadb.Client()
collection = client.create_collection(name="docs")

# Store each chunk using custom embeddings
for i, chunk in enumerate(chunks):
    input_ids = tokenizer.encode(chunk, return_tensors="pt")
    with torch.no_grad():
        outputs = model(input_ids)
        encoded = outputs.last_hidden_state[0, 1:-1]  # Ignore [CLS] and [SEP]
        embedding = encoded.mean(dim=0).tolist()

    collection.add(ids=[str(i)], embeddings=[embedding], documents=[chunk])

# Generate an embedding for a query
query = "Objeto"
input_ids = tokenizer.encode(query, return_tensors="pt")
with torch.no_grad():
    outputs = model(input_ids)
    encoded = outputs.last_hidden_state[0, 1:-1]
    query_embedding = encoded.mean(dim=0).tolist()

# Search for the most relevant document
results = collection.query(query_embeddings=[query_embedding], n_results=5)

print(results["documents"])
