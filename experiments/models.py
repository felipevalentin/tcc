from pydantic import BaseModel


class Sample(BaseModel):
    codigo: str
    titulo: str
    data: str
    cod_registro_info_sfinge: str
    municipio: str
    entidade: str
    categoria: str
    link: str
    texto: str
    url: str


class GroundTruthDOMFields(BaseModel):
    titulo: str
    data: str
    cod_registro_info_sfinge: str
    municipio: str
    entidade: str
    categoria: str


class GroundTruthExtractedFields(BaseModel):
    municipio: str
    modalidade: str
    nr_modalidade: str
    objeto: str
    justificativa: str
    data_abertura: str
    informacoes: str
    signatario: str
    cargo_do_signatario: str
