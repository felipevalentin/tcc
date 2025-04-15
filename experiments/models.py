from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from municipios import Município


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
    ELETRONICA = "Eletrônica"
    PRESENCIAL = "Presencial"


class NomeDoDocumento(StrEnum):
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


class Licitação(BaseModel):
    raciocínio: str
    nome_do_documento: NomeDoDocumento
    numero_do_processo_licitatório: str
    município: Município
    modalidade: Modalidade
    formato_da_modalidade: Optional[FormatoDaModalidade]
    número_da_modalidade: str
    objeto: str
    data_de_abertura: Optional[datetime]
    informações_do_edital: Optional[str]
    signatário: Optional[str]
    cargo_do_signatário: Optional[str]


class GroundTruth(BaseModel):
    codigo: str = Field(alias="Código")
    titulo: str = Field(alias="Título")
    nome_do_documento: str = Field(alias="Tipo de Documento")
    numero_do_processo_licitatório: str = Field(alias="NrProLicitatório")
    data_hora_dom: str = Field(alias="DataHoraDOM")
    cod_registro_info_sfinge: Optional[str] = Field(alias="cod_registro_info_sfinge")
    município: Optional[str] = Field(alias="Município")
    entidade: str = Field(alias="Entidade")
    categoria_dom: str = Field(alias="CategoriaDOM")
    modalidade: str = Field(alias="Modalidade")
    formato_da_modalidade: Optional[str] = Field(alias="Formato")
    número_da_modalidade: str = Field(alias="NrModalidade")
    objeto: str = Field(alias="Objeto")
    data_de_abertura: Optional[str] = Field(alias="Data Abertura")
    data_de_abertura_normalizada: Optional[datetime] = Field(
        alias="Data Abertura Normalizada"
    )
    informações_do_edital: Optional[str] = Field(alias="Informacoes")
    signatário: Optional[str] = Field(alias="Signatário")
    cargo_do_signatário: Optional[str] = Field(alias="Cargo do Signatário")
