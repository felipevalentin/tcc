from typing import Optional

from pydantic import BaseModel, Field


class Sample(BaseModel):
    codigo: str
    titulo: str
    data: str
    cod_registro_info_sfinge: Optional[str] = None
    municipio: Optional[str] = None
    entidade: str
    categoria: str
    link: str
    texto: str
    url: str


class GroundTruthDOMFields(BaseModel):
    titulo: str
    data_hora_dom: str
    cod_registro_info_sfinge: str
    municipio: str
    entidade: str
    categoria_dom: str


class GroundTruthExtractedFields(BaseModel):
    municipio: str
    modalidade: str
    nr_modalidade: str
    objeto: str
    justificativa: str
    data_abertura: Optional[str]
    informacoes: Optional[str]
    signatario: Optional[str]
    cargo_do_signatario: Optional[str]


class GroundTruth(BaseModel):
    codigo: str = Field(alias="Código")
    titulo: str = Field(alias="Título")
    data_hora_dom: str = Field(alias="DataHoraDOM")
    cod_registro_info_sfinge: Optional[str] = Field(alias="cod_registro_info_sfinge")
    municipio: str = Field(alias="Município")
    entidade: str = Field(alias="Entidade")
    categoria_dom: str = Field(alias="CategoriaDOM")
    modalidade: str = Field(alias="Modalidade")
    nr_modalidade: str = Field(alias="Nr.Modalidade")
    objeto: Optional[str] = Field(alias="Objeto")
    justificativa: Optional[str] = Field(alias="Justificativa")
    data_abertura: Optional[str] = Field(alias="Data Abertura")
    informacoes: Optional[str] = Field(alias="Informacoes")
    signatario: Optional[str] = Field(alias="Signatário")
    cargo_signatario: Optional[str] = Field(alias="Cargo do Signatário")
