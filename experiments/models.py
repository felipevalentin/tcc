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


class FormatoModalidade(StrEnum):
    ELETRONICO = "Eletrônico"
    PRESENCIAL = "Presencial"


class TipoDocumento(StrEnum):
    APOSTILAMENTO = "Apostilamento"
    ATA = "Ata"
    AVISO_DE_LICITACAO = "Aviso de Licitação"
    CONTRATO = "Contrato"
    EDITAL = "Edital"
    ERRATA = "Errata"
    JULGAMENTO = "Julgamento"
    LICITACAO = "Licitação"
    RATIFICACAO = "Ratificacao"
    RESULTADO = "Resultado"
    SUSPENSAO = "Suspensão"
    TERMO_ADITIVO = "Termo Aditivo"
    TERMO_DE_ADJUCACAO = "Termo de Adjucação"
    TERMO_DE_HOMOLOGACAO = "Termo de Homologação"


class GroundTruthExtractedFields(BaseModel):
    tipo_documento: TipoDocumento
    nr_processo_licitatorio: str = Field(
        description="Número do processo, exemplo processo administrativo 14/2023. Apenas o 14/2023"
    )
    municipio: Municipio = Field(
        description="Nome do município onde a licitação foi realizada"
    )
    modalidade: Modalidade = Field(description="Modalidade da Licitação")
    formato_modalidade: Optional[FormatoModalidade] = Field(
        default=None, description="O formato da modalidade"
    )
    nr_modalidade: str = Field(
        description="Número da Modalidade, exemplo pregrão eletronico 123/2024. Apenas o 123/2024"
    )
    objeto: str = Field(
        description="Descrição do objeto da licitação completa, incluindo todos detalhes"
    )
    data_abertura: Optional[datetime] = Field(
        default=None,
        description="Data de abertura da licitação, exemplo 2025-04-05T19:29",
    )
    informacoes: Optional[str] = Field(
        default=None, description="Informações onde é possível encontrar o Edital"
    )
    signatario: Optional[str] = Field(description="Nome do signatário do documento")
    cargo_do_signatario: Optional[str] = Field(description="Cargo do signatário")


class GroundTruth(BaseModel):
    codigo: str = Field(alias="Código")
    titulo: str = Field(alias="Título")
    tipo_documento: str = Field(alias="Tipo de Documento")
    nr_processo_licitatorio: str = Field(alias="NrProLicitatório")
    data_hora_dom: str = Field(alias="DataHoraDOM")
    cod_registro_info_sfinge: Optional[str] = Field(alias="cod_registro_info_sfinge")
    municipio: Optional[str] = Field(alias="Município")
    entidade: str = Field(alias="Entidade")
    categoria_dom: str = Field(alias="CategoriaDOM")
    modalidade: str = Field(alias="Modalidade")
    localidade: Optional[str] = Field(alias="Formato")
    nr_modalidade: str = Field(alias="NrModalidade")
    objeto: str = Field(alias="Objeto")
    data_abertura: Optional[str] = Field(alias="Data Abertura")
    data_abertura_normalizada: Optional[datetime] = Field(
        alias="Data Abertura Normalizada"
    )
    informacoes: Optional[str] = Field(alias="Informacoes")
    signatario: Optional[str] = Field(alias="Signatário")
    cargo_do_signatario: Optional[str] = Field(alias="Cargo do Signatário")

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
