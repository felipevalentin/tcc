from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field

from data.municipios import Municipio


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


class FormatoDaModalidade(StrEnum):
    ELETRONICA = "Eletrônico"
    PRESENCIAL = "Presencial"


class TipoDoDocumento(StrEnum):
    APOSTILAMENTO = "Apostilamento"
    ANULACAO = "Anulação"
    ATA_DE_REGISTRO_DE_PRECOS = "Ata de Registro de Preços"
    ATA_DE_RECEBIMENTO_E_ABERTURA = "Ata de Recebimento e Abertura"
    ADJUCACAO = "Adjucação"
    AVISO_DE_LICITACAO = "Aviso de Licitação"
    AVISO_DE_SUSPENSAO = "Aviso de Suspensão"
    AVISO_DE_CANCELAMENTO = "Aviso de Cancelamento"
    CONTRATO = "Contrato"
    EDITAL = "Edital"
    ERRATA = "Errata"
    TERMO_DE_HOMOLOGACAO = "Homologação"
    TERMO_ADITIVO = "Aditivo"
    JULGAMENTO = "Julgamento"
    RESULTADO = "Resultado"
    RATIFICACAO = "Ratificação"


class Raciocínio(BaseModel):
    nome_do_documento: str
    numero_do_processo_administrativo: str
    município: str
    modalidade: str
    formato_da_modalidade: str
    número_da_modalidade: str
    objeto: str
    data_de_abertura: str
    site_do_edital: str
    signatário: str
    cargo_do_signatário: str


class LicitacaoV0(BaseModel):
    tipo_do_documento: TipoDoDocumento
    numero_do_processo_licitatorio: str
    municipio: Municipio
    modalidade: Modalidade
    formato_da_modalidade: Optional[FormatoDaModalidade]
    numero_da_modalidade: str
    objeto: str
    data_de_abertura: Optional[str]
    site_do_edital: Optional[str]
    signatario: Optional[str]
    cargo_do_signatario: Optional[str]


class LicitacaoV1(BaseModel):
    tipo_do_documento: TipoDoDocumento
    numero_do_processo_licitatorio: str = Field(pattern=r"^[0-9]+/[0-9]+$")
    municipio: Municipio
    modalidade: Modalidade
    formato_da_modalidade: Optional[FormatoDaModalidade]
    numero_da_modalidade: str = Field(pattern=r"^[0-9]+/[0-9]+$")
    objeto: str
    data_de_abertura: Optional[str] = Field(
        pattern=r"^20[0-4][0-9]-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])T(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$"
    )
    site_do_edital: Optional[str]
    signatario: Optional[str]
    cargo_do_signatario: Optional[str]


class LicitacaoV2(BaseModel):
    tipo_do_documento: TipoDoDocumento
    numero_do_processo_licitatorio: str = Field(pattern=r"^[0-9]+/[0-9]+$")
    modalidade: Modalidade
    formato_da_modalidade: Optional[FormatoDaModalidade]
    numero_da_modalidade: str = Field(pattern=r"^[0-9]+/[0-9]+$")
    objeto: str
    data_de_abertura: Optional[str] = Field(
        pattern=r"^20[0-4][0-9]-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])T(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$"
    )
    site_do_edital: Optional[str]
    signatario: Optional[str]
    cargo_do_signatario: Optional[str]


class LicitacaoV3(BaseModel):
    raciocinio: str
    tipo_do_documento: TipoDoDocumento
    numero_do_processo_licitatorio: str = Field(pattern=r"^[0-9]+/[0-9]+$")
    modalidade: Modalidade
    formato_da_modalidade: Optional[FormatoDaModalidade]
    numero_da_modalidade: str = Field(pattern=r"^[0-9]+/[0-9]+$")
    objeto: str
    data_de_abertura: Optional[str] = Field(
        pattern=r"^20[0-4][0-9]-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])T(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$"
    )
    site_do_edital: Optional[str]
    signatario: Optional[str]
    cargo_do_signatario: Optional[str]


class GroundTruth(BaseModel):
    codigo: str = Field(alias="Código")
    titulo: str = Field(alias="Título")
    tipo_do_documento: Optional[str] = Field(alias="Tipo de Documento")
    numero_do_processo_licitatorio: str = Field(alias="NrProLicitatório")
    data_hora_dom: str = Field(alias="DataHoraDOM")
    cod_registro_info_sfinge: Optional[str] = Field(alias="cod_registro_info_sfinge")
    municipio: Optional[str] = Field(alias="Município")
    entidade: str = Field(alias="Entidade")
    categoria_dom: str = Field(alias="CategoriaDOM")
    modalidade: str = Field(alias="Modalidade")
    formato_da_modalidade: Optional[str] = Field(alias="Formato")
    numero_da_modalidade: str = Field(alias="NrModalidade")
    objeto: str = Field(alias="Objeto")
    data_de_abertura: Optional[datetime] = Field(alias="Data Abertura Normalizada")
    site_do_edital: Optional[str] = Field(alias="Informacoes")
    signatario: Optional[str] = Field(alias="Signatário")
    cargo_do_signatario: Optional[str] = Field(alias="Cargo do Signatário")
