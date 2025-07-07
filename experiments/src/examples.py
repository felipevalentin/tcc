import os
from typing import List, Tuple

import chromadb
import torch
from chromadb.config import Settings
from transformers import AutoModel, AutoTokenizer

CHROMA_PATH = "./chroma/examples"
EXAMPLES = [
    {
        "input": """## Nome do Documento
PUBLICAÇÃO DE HOMOLOGAÇÃO DE PREGÃO ELETRÔNICO Nº PMC 89/2023

## Texto do Documento
MUNICÍPIO DE CANOINHAS

Compras e Contratos

Termo Adjudicação - Homologação e Adjudicação

Pág 1 / 1

IPM Sistemas Ltda

Atende.Net - WCO v:2015.04

Identificador: WCO901201-31008-RKWCEFIAEPXQ-8 - Emitido por: DAVI HINKE SOARES 26/01/2024 10:50:39 -03:00

TERMO DE HOMOLOGAÇÃO E ADJUDICAÇÃO

01 - Homologar e Adjudicar a presente Licitação nestes termos:

Nr. Processo: 3706/2023

Nr. Licitação: 89/2023

Modalidade: Pregão Eletrônico

Tipo Concorrência: Registro de Preços

Data da homologação: 26/01/2024

Objeto da Licitação: REGISTRO DE PREÇOS PARA FORNECIMENTO, COLOCAÇÃO DE UMA 

QUANTIDADE ESTIMADA DE 1.700 METROS LINEARES DE MURO PRÉ 

FABRICADO COM ALTURA DE 2,05M, DESTINADOS AS DIVERSAS 

SECRETARIAS, FUNDOS E FUNDAÇÕES MUNICIPAIS, CORPO DE BOMBEIROS, 

POLÍCIA MILITAR E CIVIL.

02 - Fornecedores:

10053 - CIMENTELA IND DE TELAS E ARTEF.DE CONCRETO LTDA ME - 78.527.645/0001-74

Sem Lote

Item Produto Unidade Marca Quantidade Valor Unitário Valor Total

1 MURO PRÉ- FABRICADO M PROPRIA  

PRÉ-

FABRICADO

1700 R$371,00 R$630.700,00

Total do Lote: R$630.700,00

Total do Fornecedor: R$630.700,00

03 -  Autorizar a emissão da(s) nota(s) de empenho correspondente(s):

Canoinhas, 26 de janeiro de 2024.

___________________________________

RAFAEL ROTTILI ROEDER

Secretário de Planejamento
""",
        "output": """{
    "tipo_do_documento": "Homologação",
    "numero_do_processo_licitatório": "3706/2023",
    "município": "Canoinhas",
    "modalidade": "Pregão",
    "formato_da_modalidade": "Eletrônico",
    "número_da_modalidade": "89/2023",
    "objeto": "MURO PRÉ- FABRICADO M PROPRIA",
    "data_de_abertura": null,
    "site_do_edital": null,
    "signatário": RAFAEL ROTTILI ROEDER",
    "cargo_do_signatário": "Secretário de Planejamento"
}""",
    },
    {
        "input": """## Nome do Documento
AVISO DE LICITAÇÃO PREGÃO ELETRÔNICO Nº 6/2023 FUMSCI

## Texto do Documento
PREFEITURA DE NAVEGANTES –

PREGÃO ELETRONICO Nº 6/2023 FUMSCI 

Comunicamos na forma da lei 8.666/93 e suas alterações, que se encontra aberto o processo licitatório do objeto: Pregão Eletrônico para Registro de Preço visando a contratação de empresa especializada em prestação de serviço na manutenção corretiva, preventiva e estética na área mecânica, funilaria, pintura(c/adesivação), elétrica(eletrônica), tapeçaria e borracharia de veículos automotores com fornecimento e substituição de peças, materiais e acessórios em estado novo, originais dos fabricantes das marcas dos veículos e com desconto de 5% (cinco por cento) sobre os preços das tabelas e catálogos dos fabricantes ou revendas autorizadas, para atender a manutenção da frota das Secretarias, Fundos, Fundações, Polícia Militar e Corpo de Bombeiros Militar de Navegantes. Interessados deverão cadastrar-se no site 

http://bnc.org.br/cadastro/. 

Entrega das propostas a partir do dia 19/05/2023 até às 13h30 do dia 31/05/2023. Início da sessão em meio eletrônico às 14

h00 do dia 31/05/2023. O edital se encontra à disposição na Rua João Emílio nº 100, Navegantes/SC e no site: 

www.navegantes.sc.gov.br link fornecedor. Libardoni Fronza – Prefeito.
""",
        "output": """{
    "tipo_do_documento": "Aviso de Licitação",
    "numero_do_processo_licitatório": "6/2023",
    "município": "Navegantes",
    "modalidade": "Pregão",
    "formato_da_modalidade": Eletrônico,
    "número_da_modalidade": "6/2023",
    "objeto": "Pregão Eletrônico para Registro de Preço visando a contratação de empresa especializada em prestação de serviço na manutenção corretiva, preventiva e estética na área mecânica, funilaria, pintura(c/adesivação), elétrica(eletrônica), tapeçaria e borracharia de veículos automotores com fornecimento e substituição de peças, materiais e acessórios em estado novo, originais dos fabricantes das marcas dos veículos e com desconto de 5% (cinco por cento) sobre os preços das tabelas e catálogos dos fabricantes ou revendas autorizadas, para atender a manutenção da frota das Secretarias, Fundos, Fundações, Polícia Militar e Corpo de Bombeiros Militar de Navegantes",
    "data_de_abertura": "2023-05-31T14:00",
    "site_do_edital": "www.navegantes.sc.gov.br",
    "signatário": "Libardoni Fronza",
    "cargo_do_signatário": "Prefeito"
}""",
    },
    {
        "input": """## Nome do Documento
PL 55 DISPENSA DE LICITAÇÃO 24- 2024 - SABONETE

## Texto do Documento
MUNICÍPIO DE IPUMIRIM

ESTADO DE SANTA CATARINA

AVISO DE DISPENSA DE LICITAÇÃO Nº 24/2024

PROCESSO DE LICITAÇÃO Nº 55/2024

HILÁRIO REFFATTI,

PREFEITO MUNICIPAL, torna público para conhecimento dos interessados que realizou 

 DISPENSA DE LICITAÇÃO, na forma da Lei nº 14.133, de 1º de abril de 2021 e Decreto Municipal Nº 2.793/2023.

 

O objeto da licitação é: 

Aquisição de sabonete líquido neutro para atender as necessidades da Secretaria de Educação, Cultura e Esportes.



. Possíveis alterações, suspensão, revogação ou anulação do processo de dispensa será disponibilizada nos endereços eletrônicos acima mencionados, cabendo às licitantes interessadas acompanhar o andamento da licitação. 

 

Ipumirim, 30/04/2024

""",
        "output": """{
    "nome_do_documento": "Dispensa de Licitação",
    "numero_do_processo_licitatório": "55/2024",
    "município": "Ipumirim",
    "modalidade": "Dispensa de Licitação",
    "formato_da_modalidade": null,
    "número_da_modalidade": "24/2024",
    "objeto": "Aquisição de sabonete líquido neutro para atender as necessidades da Secretaria de Educação, Cultura e Esportes."
    "data_de_abertura": null,
    "site_do_edital": null,
    "signatário": null,
    "cargo_do_signatário": null
}""",
    },
]

ONE_SHOT = f"#Exemplos\n## Entrada\n{EXAMPLES[0]['input']} \n\n ## Saída\n{EXAMPLES[0]['output']}"
ONE_SHOT_OUT = f"#Exemplos\n# Saída\n{EXAMPLES[0]['output']}"
FEW_SHOT = f"#Exemplos\n## Entrada\n{EXAMPLES[0]['input']} \n\n ## Saída\n{EXAMPLES[0]['output']}\n\n## Entrada\n{EXAMPLES[1]['input']} \n\n ## Saída\n{EXAMPLES[1]['output']}\n\n## Entrada\n{EXAMPLES[2]['input']} \n\n ## Saída\n{EXAMPLES[2]['output']}"
FEW_SHOT_OUT = f"# Exemplos\n## Saída\n{EXAMPLES[0]['output']}\n\n## Saída\n{EXAMPLES[1]['output']}\n\n ## Saída\n{EXAMPLES[2]['output']}"
SPECIFIC_ONE_SHOT = (
    f"# Exemplos\n## Entrada\n{EXAMPLES[1]['input']}## Saída\n{EXAMPLES[1]['output']}"
)
SPECIFIC_ONE_SHOT_OUT = f"# Exemplos\n## Saída\n{EXAMPLES[1]['output']}"
SPECIFIC_FEW_SHOT = f"# Exemplos\n## Entrada\n{EXAMPLES[1]['input']}\n\n## Saída\n{EXAMPLES[1]['output']}\n\n## Entrada\n{EXAMPLES[2]['input']}\n\n## Saída\n{EXAMPLES[2]['output']}"
SPECIFIC_FEW_SHOT_OUT = (
    f"#Exemplos\n## Saída\n{EXAMPLES[1]['output']}\n\n## Saída\n{EXAMPLES[2]['output']}"
)
CHAIN_OF_THOUGHT = (
    f"Pense no passo a passo da extração preenchendo o campo de raciocínio"
)


def get_model_and_tokenizer():
    model = AutoModel.from_pretrained("neuralmind/bert-large-portuguese-cased")
    tokenizer = AutoTokenizer.from_pretrained(
        "neuralmind/bert-large-portuguese-cased", do_lower_case=False
    )
    return model, tokenizer


def compute_embedding(text: str, model, tokenizer) -> List[float]:
    input_ids = tokenizer.encode(
        text, return_tensors="pt", truncation=True, max_length=512
    )
    with torch.no_grad():
        outputs = model(input_ids)
        encoded = outputs.last_hidden_state[0, 1:-1]
        return encoded.mean(dim=0).tolist()


def setup_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)


def setup_chroma_db(examples: List[dict], model, tokenizer):
    client = setup_chroma_client()
    collection_name = "examples"

    try:
        collection = client.get_collection(collection_name)
        print("✅ Collection already exists. Using existing collection.")
    except:
        print("📦 Creating new collection with examples.")
        collection = client.create_collection(name=collection_name)
        for i, ex in enumerate(examples):
            embedding = compute_embedding(ex["input"], model, tokenizer)
            collection.add(
                ids=[str(i)],
                documents=[ex["input"]],
                embeddings=[embedding],
                metadatas=[{"output": ex["output"]}],
            )
    return collection


def find_best_example(text: str, collection, model, tokenizer) -> Tuple[str, str, str]:
    query_embedding = compute_embedding(text, model, tokenizer)
    results = collection.query(query_embeddings=[query_embedding], n_results=1)
    best_id = results["ids"][0][0]
    best_input = results["documents"][0][0]
    best_output = results["metadatas"][0][0]["output"]
    return best_id, best_input, best_output


model, tokenizer = get_model_and_tokenizer()
collection = setup_chroma_db(EXAMPLES, model, tokenizer)


def dynamic_example(new_text):
    best_id, best_input, best_output = find_best_example(
        new_text, collection, model, tokenizer
    )
    return f"#Exemplos\n## Entrada\n{best_input} \n\n ## Saída\n{best_output}"


def dynamic_example_out(new_text):
    best_id, best_input, best_output = find_best_example(
        new_text, collection, model, tokenizer
    )
    return f"#Exemplosn\n## Saída\n{best_output}"
