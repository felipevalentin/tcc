from pydantic import BaseModel

class Atributos(BaseModel):
    municipio: str
    modalidade: str
    nr_modalidade: str
    objeto: str
    justificativa: str
    data_abertura: str
    informacoes: str
    signatario: str
    cargo_do_signatario: str
