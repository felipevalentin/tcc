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
    ATA_DE_ABERTURA = "Ata de Abertura"
    AVISO_DE_LICITACAO = "Aviso de Licitação"
    CONTRATO = "Contrato"
    EDITAL = "Edital"
    ERRATA = "Errata"
    JULGAMENTO = "Julgamento"
    LICITACAO = "Licitação"
    RATIFICACAO = "Ratificacao"
    # RESULTADO = "Resultado"
    SUSPENSAO = "Suspensão"
    TERMO_ADITIVO = "Termo Aditivo"
    TERMO_DE_ADJUCACAO = "Termo de Adjucação"
    TERMO_DE_HOMOLOGACAO = "Termo de Homologação"

class GroundTruthExtractedFields(BaseModel):
    model_config = ConfigDict(title='Licitação')
    reasoning: str = Field(title='Reasoning', description="Any reasoning need you can put here")
    tipo_documento: TipoDocumento = Field(
        title="Tipo de Documento",
        description="Presente no título do documento",
    )
    nr_processo_licitatorio: str = Field(
        title="Número Processo Licitatório",
        description="Processo administrativo 'numero/ano'",
        pattern="^[0-9]+/[0-9]{4}$"
    )
    municipio: Municipio = Field(
        title="Município",
        description="Nome do município de Santa Catarina onde ocorreu a licitação",
    )
    modalidade: Modalidade = Field(
        title="Modalidade",
        description="Modalidade da Licitação",
    )
    formato_modalidade: Optional[FormatoModalidade] = Field(
        title="Formato da Modalidade",
        default=None, description="Modalidade formato_modalidade",
    )
    nr_modalidade: str = Field(
        title="Número da Modalidade",
        description="Modalidade formato_modalidade 'numero/ano'",
        pattern="^[0-9]+/[0-9]{4}$"

    )
    objeto: str = Field(
        title="Objeto",
        description="Descrição do objeto da licitação completa, incluindo todos detalhes",
    )
    data_abertura: Optional[datetime] = Field(
        title="Data de abertura",
        default=None,
        description="Data de abertura",
    )
    informacoes: Optional[str] = Field(
        title="Informações",
        default=None, description="Site onde é possível encontrar o Edital",
    )
    signatario: Optional[str] = Field(
        title="Signatário",
        default=None, description="Nome de quem assinou o documento",
    )
    cargo_do_signatario: Optional[str] = Field(
        title="Cargo do Signtário",
        default=None, description="Cargo de quem assinou o documento",
    )


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
    formato_modalidade: Optional[str] = Field(alias="Formato")
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
