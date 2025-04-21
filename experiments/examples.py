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
EXAMPLE_1_OUTPUT = """{
    "tipo_do_documento": "Termo de Homologação",
    "numero_do_processo_licitatório": "34/2022",
    "município": "Curitibanos",
    "modalidade": "Pregão",
    "formato_da_modalidade": "Eletrônica",
    "número_da_modalidade": "34/2022",
    "objeto": "AQUISIÇÃO DE SISTEMA DE INFORMÁTICA PARA REGISTRO, TRATAMENTO E TRANSMISSÃO DE DADOS DOS SERVIÇOS E ATENDIMENTOS DE SAÚDE NO ÂMBITO DO MUNICÍPIO DE CURITIBANOS",
    "data_de_abertura": 2022-06-23T13:16,
    "informações_do_edital": www.curitibanos.sc.gov.br,
    "signatário": Roque Stanguerlin,
    "cargo_do_signatário": Presidente do Fundo
}"""

EXAMPLE_2 = """Titulo: EXTRATO SEGUNDO TERMO ADITIVO DE PRAZO AO CONTRATO Nº 034/SAMAE/2023 DO PROCESSO DE LICITAÇÃO Nº 053/SAMAE/2023 - PREGÃO Nº 027/SAMAE/2023
Corpo: EXTRATO TERMO CONTRATO
SERVIÇO AUTÔNOMO MUNICIPAL DE ÁGUA E ESGOTO
TIJUCAS - Santa Catarina                                                                                                                   
EXTRATO SEGUNDO TERMO ADITIVO DE PRAZO AO CONTRATO Nº 034/SAMAE/2023
DO PROCESSO DE LICITAÇÃO Nº 053/SAMAE/2023 - PREGÃO Nº 027/SAMAE/2023.
CONTRATANTE: SAMAE - SERVIÇO AUTÔNOMO MUNICIPAL DE ÁGUA E ESGOTO.
CONTRATADO:LUCCA COMUNICAÇÃO VISUAL E ESTRUTURAS EIRELI.
OBJETO: CONTRATAÇÃO DE EMPRESA ESPECIALIZADA EM FORNECIMENTO E INSTALAÇÃO DE GUARDA-CORPOS EM AÇO GALVANIZADO, PARA O SAMAE- SERVIÇO AUTÔNOMO MUNICIPAL DE ÁGUA E ESGOTO, DO MUNICÍPIO DE TIJUCAS/SC.
DO PRAZO: FICA RENOVADO O CONTRATO ADMINISTRATIVO Nº 034/SAMAE/2023 POR MAIS UM PERÍODO DE 90 (NOVENTA) DIAS, INICIANDO-SE EM 01/01/2024, COM TÉRMINO EM 31/03/2024.
TIJUCAS/SC, 18 DE DEZEMBRO DE 2023."""

EXAMPLE_2_OUTPUT = """{
    "nome_do_documento": "Termo de Aditivo",
    "numero_do_processo_licitatório": "53/2023",
    "município": "Tíjucas",
    "modalidade": "Pregão",
    "formato_da_modalidade": null,
    "número_da_modalidade": "27/2023",
    "objeto": "CONTRATAÇÃO DE EMPRESA ESPECIALIZADA EM FORNECIMENTO E INSTALAÇÃO DE GUARDA-CORPOS EM AÇO GALVANIZADO, PARA O SAMAESERVIÇO AUTÔNOMO MUNICIPAL DE ÁGUA E ESGOTO, DO MUNICÍPIO DE TIJUCAS/SC.",
    "data_de_abertura": null,
    "informações_do_edital": null,
    "signatário": null,
    "cargo_do_signatário": null
}"""

EXAMPLE_3 = """Titulo: AVISO LICITAÇÃO CC 269-2024 SERVIDÃO ADEMIR GOMES
Corpo: Microsoft Word - CC Nº 269- 2024 Servidão Ademir Gomes
ESTADO DE SANTA CATARINA 
PREFEITURA MUNICIPAL DE PALHOÇA 
AVISO DE LICITAÇÃO 
3698F1F6DC17048681CB80777927E5E44C1A1DBD 
Modalidade: Concorrência Pública nº 269/2024/ PMP 
Objeto: Contratação de empresa para execução de 
DRENAGEM, PAVIMENTAÇÃO EM PAVER E 
SINZALIZAÇÃO VIÁRIA VERTICAL, localizada na 
SERVIDÃO ADEMIR GOMES, Bairro BELA VISTA, 
Palhoça/SC, incluindo fornecimento de material e mão de 
obra, nos termos do Termo de Referência, conforme condições 
e exigências estabelecidas neste instrumento e seus anexos 
Abertura: Dia 16/12/2024 às 13h30min (horário de Brasília) 
Local da retirada do Edital e Anexos: 
www.palhoca.sc.gov.br e Portal de Compras Públicas 
Palhoça, 29 de novembro de 2024. 
EDUARDO FRECCIA 
PREFEITO MUNICIPAL"""

EXAMPLE_3_OUTPUT = """{
    "nome_do_documento": "Aviso de Licitação",
    "numero_do_processo_licitatório": "269/2024",
    "município": "Palhoça",
    "modalidade": "Concorrência",
    "formato_da_modalidade": null,
    "número_da_modalidade": "27/2023",
    "objeto": "Contratação de empresa para execução de DRENAGEM, PAVIMENTAÇÃO EM PAVER E SINZALIZAÇÃO VIÁRIA VERTICAL, localizada na SERVIDÃO ADEMIR GOMES, Bairro BELA VISTA, Palhoça/SC, incluindo fornecimento de material e mão de obra, nos termos do Termo de Referência, conforme condições e exigências estabelecidas neste instrumento e seus anexos ",
    "data_de_abertura": 2024-12-16T13:30,
    "site_do_edital": "www.palhoca.sc.gov.br",
    "signatário": EDUARDO FRECCIA,
    "cargo_do_signatário": PREFEITO MUNICIPAL
}"""
