from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from municipios import Municipio


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


class Modalidade(StrEnum):
    CONCORRENCIA = "Concorrência"
    CONCURSO = "Concurso"
    CONVITE = "Convite"
    CREDENCIAMENTO = "Credenciamento"
    DIALOGO_COMPETITIVO = "Diálogo Competitivo"
    DISPENSA_DE_LICITACAO = "Dispensa de Licitação"
    INEXIGIBILIDADE = "Inexigibilidade"
    LEILAO = "Leilão"
    REGIME_DIFERENCIADO_DE_CONTRATACOES = "Regime Diferenciado de Contratações"
    PREGAO = "Pregão"
    TOMADA_DE_PRECOS = "Tomada de Preços"


class Formato(StrEnum):
    ELETRONICO = "Eletrônico"
    PRESENCIAL = "Presencial"


class GroundTruthExtractedFields(BaseModel):
    municipio: Municipio = Field(description="Nome do município onde a licitação foi realizada")
    modalidade: Modalidade = Field(description="Modalidade da Licitação")
    formato: Optional[Formato] = Field(default=None, description="O Formato da Modalidade")
    nr_modalidade: str = Field(description="Número da Modalidade, exemplo 123/2024")
    objeto: str = Field(description="Descrição do objeto da licitação")
    justificativa: Optional[str] = Field(default=None, description="Justificativa apresentada para a realização da licitação")
    data_abertura: Optional[datetime] = Field(default=None, description="Data de abertura da licitação, exmeplo 2025-04-05T19:29")
    informacoes: Optional[str] = Field(default=None, description="Informações adicionais relevantes")
    signatario: str = Field(description="Nome do signatário do documento")
    cargo_do_signatario: str = Field(description="Cargo do signatário")

    # @field_validator("data_abertura")
    # def validate_data_abertura(cls, value: Optional[datetime]) -> Optional[datetime]:
    #     if value is not None:
    #         if not (2000 <= value.year <= 2040):
    #             raise ValueError("data_abertura year must be between 2000 and 2040")
    #     return value
    # 2025-04-05T19:29
    # 2025-04-05T19:29:00
    # 2025-04-05T19:29:00+00:00
    # ano 2025 mes 04 dia 05 hora 19 minuto 29


class GroundTruth(BaseModel):
    codigo: str = Field(alias="Código")
    titulo: str = Field(alias="Título")
    nr_pro_licitatorio: str = Field(alias="NrProLicitatório")
    data_hora_dom: str = Field(alias="DataHoraDOM")
    cod_registro_info_sfinge: Optional[str] = Field(alias="cod_registro_info_sfinge")
    municipio: str = Field(alias="Município")
    entidade: str = Field(alias="Entidade")
    categoria_dom: str = Field(alias="CategoriaDOM")
    modalidade: str = Field(alias="Modalidade")
    formato: Optional[str] = Field(alias="Formato")
    nr_modalidade: str = Field(alias="NrModalidade")
    objeto: str = Field(alias="Objeto")
    justificativa: Optional[str] = Field(alias="Justificativa")
    data_abertura: Optional[str] = Field(alias="Data Abertura")
    data_abertura_normalizada: Optional[str] = Field(alias="Data Abertura Normalizada")
    informacoes: Optional[str] = Field(alias="Informacoes")
    signatario: str = Field(alias="Signatário")
    cargo_do_signatario: str = Field(alias="Cargo do Signatário")
